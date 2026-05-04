# --- Import all necessary libraries for our entire adventure ---
import os
import re
import asyncio
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from typing import Optional

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import google.generativeai as genai
from google.adk.agents import Agent, SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools import google_search, ToolContext
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part

print("✅ All libraries are ready to go!")


def _env_truthy(name: str) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return False
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _normalize_api_key(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1].strip()
    return s or None


# Vertex AI: uses Application Default Credentials (no Gemini API key).
# Gemini API: uses GOOGLE_API_KEY (AI Studio).
use_vertex = _env_truthy("GOOGLE_GENAI_USE_VERTEXAI")
api_key = _normalize_api_key(os.getenv("GOOGLE_API_KEY"))

if use_vertex:
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    if not project or not location:
        print(
            "⚠️ Vertex mode: set GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION."
        )
    else:
        print(
            f"✅ Vertex mode (no API key): project={project!r}, location={location!r}."
        )
else:
    if not api_key:
        print(
            "⚠️ Gemini API mode: set GOOGLE_API_KEY, or enable Vertex with "
            "GOOGLE_GENAI_USE_VERTEXAI=TRUE."
        )
    genai.configure(api_key=api_key)
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    print("✅ Gemini API mode: using GOOGLE_API_KEY.")

# --- A Helper Function to Run Our Agents ---
# We'll use this function throughout the notebook to make running queries easy.

async def run_agent_query(agent: Agent, query: str, session: Session, user_id: str, is_router: bool = False):
    """Initializes a runner and executes a query for a given agent and session."""
    print(f"\n🚀 Running query for agent: '{agent.name}' in session: '{session.id}'...")

    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name=agent.name
    )

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=Content(parts=[Part(text=query)], role="user")
        ):
            if not is_router:
                # Let's see what the agent is thinking!
                print(f"EVENT: {event}")
            if event.is_final_response():
                final_response = event.content.parts[0].text
    except Exception as e:
        final_response = f"An error occurred: {e}"

    if not is_router:
        print("\n" + "-"*50)
        print("✅ Final Response:")
        print(final_response)
        print("-"*50 + "\n")

    return final_response

# --- Initialize our Session Service ---
# This one service will manage all the different sessions in our notebook.
session_service = InMemorySessionService()
my_user_id = "adk_adventurer_001"

# --- Agent Definitions for our Specialist Team ---
# --- Agent Definition ---

certification_path_agent = Agent(
    name="certification_path_agent",
    model="gemini-2.5-flash",
    description="Expert architect specialized in designing personalized certification roadmaps for AI, Cloud, and Security based on career goals and current experience.",
    instruction="""
    You are the "Career Path Architect" 🎓 - a specialized AI assistant that builds strategic certification roadmaps.

    Your Mission:
    To map out a logical sequence of professional certifications (AI, Cloud, Security) that bridges a user's current skills to their dream job, ensuring maximum ROI and industry relevance.

    Guidelines:
    1. **Tier-Based Progression**: Organize paths into 'Foundational', 'Associate', and 'Professional/Expert' levels. Do not suggest expert exams without checking for prerequisites.
    2. **Multi-Vendor Strategy**: Be objective. If a user wants 'Cloud', compare AWS, Azure, and GCP paths. If they want 'Security', include vendor-neutral options like CompTIA or ISC2.
    3. **Time & Cost Estimates**: Use Google Search to find current exam costs and recommended study hours for each certification.
    4. **Market Relevancy**: Search for current job market trends to prioritize certifications that are currently in high demand by employers.

    RETURN the roadmap in MARKDOWN FORMAT with a clear visual flow (e.g., Step 1 -> Step 2) and include "Why this cert?" for each recommendation.
    """,
    tools=[google_search]
)

ai_certification_agent = Agent(
    name="ai_certification_agent",
    model="gemini-2.5-flash",
    tools=[google_search],
    instruction="You are an AI career strategist. Your goal is to identify the most valuable Machine Learning and Generative AI certifications based on a user's skill level. You must distinguish between foundational, associate, and professional tiers.'"
)

cloud_certification_agent = Agent(
    name="cloud_certification_agent",
    model="gemini-2.5-flash",
    tools=[google_search],
    instruction="You are a Cloud Infrastructure architect. Your task is to map out the certification journey for AWS, Azure, and GCP. You must distinguish between foundational, associate, and professional tiers. For example: 'The best entry point for multi-cloud is the **Azure Fundamentals (AZ-900)**.'"
)

security_certification_agent = Agent(
    name="security_certification_agent",
    model="gemini-2.5-flash",
    tools=[google_search],
    instruction="You are a Cybersecurity mentor. Your objective is to find certifications that validate technical proficiency in defense, penetration testing, or governance.You must distinguish between foundational, associate, and professional tiers.'"
)

# --- The Brain of the Operation: The Router Agent ---
# We update the router's instructions to know about the new 'combo' task.
router_agent = Agent(
    name="router_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a request router. Your job is to analyze a user's career or technical query and decide which certification agent is best suited to handle it.
    Do not answer the query yourself; only return the name of the most appropriate choice.

    Available Options:
    - 'ai_certification_agent': For queries about Machine Learning, Artificial Intelligence, Generative AI, or Data Science certifications.
    - 'cloud_certification_agent': For queries regarding AWS, Azure, GCP, cloud architecture, or infrastructure-as-code.
    - 'security_certification_agent': For queries about Cybersecurity, Ethical Hacking, Network Defense, or GRC (Governance, Risk, and Compliance).

    Only return the single, most appropriate option's name and nothing else.
    """
)

# We'll create a dictionary of all our individual worker agents
worker_agents = {
    "certification_path_agent": certification_path_agent,
    "ai_certification_agent": ai_certification_agent,
    "cloud_certification_agent": cloud_certification_agent,
    "security_certification_agent": security_certification_agent
}

print("🤖 Agent team assembled for sequential workflows!")

# --- Agent Definitions for our Specialist Team (Refactored for Sequential Workflow) ---

async def handle_single_query(query: str):
    """Logic to process a single query through the router and worker agents."""
    # 1. Route to the correct expert
    router_session = await session_service.create_session(app_name=router_agent.name, user_id=my_user_id)
    chosen_route = await run_agent_query(router_agent, query, router_session, my_user_id, is_router=True)
    chosen_route = chosen_route.strip().replace("'", "").replace('"', "")
    
    if chosen_route not in worker_agents:
        return f"Error: Router returned unknown agent: '{chosen_route}'"

    worker_agent = worker_agents[chosen_route]
    worker_session = await session_service.create_session(app_name=worker_agent.name, user_id=my_user_id)

    # STEP A: Generate the Roadmap
    initial_response = await run_agent_query(worker_agent, query, worker_session, my_user_id)

    # STEP B: Extract the primary certification (Expected in **Bold**)
    match = re.search(r'\*\*(.*?)\*\*', initial_response)
    target_cert = match.group(1) if match else "the recommended certification"
    
    # STEP C: Generate the 3-Month Study Plan
    study_plan_query = f"Based on the roadmap provided, generate a detailed 3-month study plan for {target_cert}. Breakdown by Month 1, Month 2, and Month 3."
    study_plan_response = await run_agent_query(worker_agent, study_plan_query, worker_session, my_user_id)

    full_combined_response = (
        f"### 🗺️ Certification Roadmap\n{initial_response}\n\n"
        f"--- \n\n"
        f"### 📅 3-Month Study Plan for {target_cert}\n{study_plan_response}"
    )
    
    return full_combined_response


async def run_sequential_app():
    queries = [
        "I want a roadmap for Generative AI and LLMs with a 3 month study plan.(beginner to Advanced)",
        "Which AWS certification is best for a beginner starting in Cloud?",
        "What are certification is best for starting in Security Field?",
        "I need a 3 month study plan to prepare for beginner Security certifications."
    ]

    # Map the router's string output to the actual Agent objects
    worker_agents = {
        "certification_path_agent": certification_path_agent,
        "ai_certification_agent": ai_certification_agent,
        "cloud_certification_agent": cloud_certification_agent,
        "security_certification_agent": security_certification_agent
    }

    for query in queries:
        print(f"\n{'='*60}\n🎓 Processing Request: '{query}'\n{'='*60}")

        # 1. Route to the correct expert
        router_session = await session_service.create_session(app_name=router_agent.name, user_id=my_user_id)
        chosen_route = await run_agent_query(router_agent, query, router_session, my_user_id, is_router=True)
        chosen_route = chosen_route.strip().replace("'", "")
        
        print(f"🚦 Router selected: '{chosen_route}'")

        if chosen_route in worker_agents:
            worker_agent = worker_agents[chosen_route]
            worker_session = await session_service.create_session(app_name=worker_agent.name, user_id=my_user_id)

            # STEP A: Generate the Roadmap
            print(f"📝 Step 1: Generating Roadmap...")
            initial_response = await run_agent_query(worker_agent, query, worker_session, my_user_id)

            # STEP B: Extract the primary certification (Expected in **Bold**)
            match = re.search(r'\*\*(.*?)\*\*', initial_response)
            target_cert = match.group(1) if match else "the recommended certification"
            
            # STEP C: Generate the 3-Month Study Plan
            print(f"📅 Step 2: Designing 3-Month Study Plan for {target_cert}...")
            study_plan_query = f"Based on the roadmap provided, generate a detailed 3-month study plan for {target_cert}. Breakdown by Month 1, Month 2, and Month 3."
            
            # This call uses the same session to maintain context
            await run_agent_query(worker_agent, study_plan_query, worker_session, my_user_id)

        else:
            print(f"🚨 Error: Router returned unknown agent: '{chosen_route}'")

root_agent = Agent(
    name="certification_router_agent",
    model="gemini-2.5-flash",
    description="A central coordinator that routes users to specialized certification experts in AI, Cloud, and Security.",
    instruction=(
        "You are the Lead Career Strategist. Your job is to analyze the user's request and "
        "determine which specialist is best suited to answer. \n\n"
        "Options:\n"
        "- 'ai_certification_agent': Use for Machine Learning, LLMs, or Data Science queries.\n"
        "- 'cloud_certification_agent': Use for AWS, Azure, GCP, or Cloud Architecture.\n"
        "- 'security_certification_agent': Use for Cybersecurity, Ethical Hacking, or GRC.\n\n"
        "Only return the name of the agent and nothing else."
    ),
    # Note: In a sequential flow, the router selects the path rather than calling tools directly.
)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Serves the frontend HTML file."""
    return send_from_directory('.', 'index.html')

@app.route('/query', methods=['POST'])
def query_endpoint():
    data = request.json
    user_query = data.get('query', '')
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    # Run the async logic in the synchronous Flask route
    response_text = asyncio.run(handle_single_query(user_query))
    return jsonify({"answer": response_text})

if __name__ == "__main__":
    print("🚀 Starting API Server on http://localhost:5000")
    app.run(port=5000, debug=False)