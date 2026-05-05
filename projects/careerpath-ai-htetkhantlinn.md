# 🚀 CareerPath AI

**Personalized Learning Roadmap Generator** powered by Google's Agent Development Kit (ADK) and Gemini 2.5 Flash. Get a custom-tailored tech career guide with skills, resources, projects, market insights, and a realistic timeline — all in seconds.

![Demo](https://github.com/Htet-Khant-Linn/careerpath-ai/blob/main/Screenshot%202026-05-03%20191808.png)

**Click Here to test** -> [CareerPath AI](https://htet-khant-linn.github.io/careerpath-ai/)
---

## 🧠 How It Works

CareerPath AI uses a **multi-agent orchestration system** to research and synthesize comprehensive career roadmaps. When you submit your target role and background, the system triggers a phased workflow:

learning_roadmap_agent (SequentialAgent)
```bash
├── parallel_research_agent (ParallelAgent)
│ ├── skills_agent # Maps foundational → advanced skills
│ ├── resources_agent # Curates courses, docs, and books
│ ├── projects_agent # Designs portfolio-building projects
│ └── market_agent # Analyzes job demand & salary data
├── timeline_agent # Organizes skills into a realistic schedule
└── synthesis_agent # Formats everything into a polished Markdown guide
```


### Three Phases

| Phase | Agent | Role |
|-------|-------|------|
| **1. Parallel Research** | `parallel_research_agent` | Four specialists simultaneously gather skills, resources, projects, and market data |
| **2. Scheduling** | `timeline_agent` | Converts raw skills into a phased, time-bound study plan |
| **3. Synthesis** | `synthesis_agent` | Compiles all outputs into an encouraging, readable roadmap |

> ⚡ **Why parallel?** The four research agents run concurrently, cutting total response time from ~20 seconds to ~5 seconds.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Google Cloud Run + ADK + Gemini 2.5 Flash |
| **Frontend** |  HTML (GitHub Pages) |
| **Orchestration** | Google Agent Development Kit (ADK) |
| **LLM** | Gemini 2.5 Flash (Google Vertex AI) |

---

## 📦 Deployment

### Prerequisites

- Google Cloud Project with billing enabled
- `gcloud` CLI installed and authenticated
- GitHub account (for frontend hosting)

---

### 1. Backend (Google Cloud Run)

Clone or create your project folder containing:
- `app.py` — Main FastAPI/Flask application
- `requirements.txt` — Python dependencies
- `Dockerfile` — Container configuration
- `.gcloudignore` — Ignore unnecessary files

In **Google Cloud Shell** or your terminal:

```bash
# Set your active project
gcloud config set project YOUR_PROJECT_ID
```

```bash
# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com
```

```bash
# Deploy to Cloud Run
gcloud run deploy careerpath-ai \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 120
```

📝 Note: *After successful deployment, Cloud Run will output a Service URL (e.g., https://careerpath-ai-xyz-uc.a.run.app). Save this for the frontend setup.*

## 2. Frontend (GitHub Pages)
Open `index.html` in a text editor

Find the **BACKEND_URL** variable and set it to your Cloud Run service URL:
```bash
const BACKEND_URL = "https://careerpath-ai-xyz-uc.a.run.app"; // No trailing slash
```

Push index.html to a GitHub repository:
```bash
git init
git add index.html
git commit -m "Deploy CareerPath AI frontend"
git branch -M main
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

Enable GitHub Pages:
- Go to repository Settings → Pages
- Under Branch, select main and / (root)
- Click Save

Access your live app at: https://your-username.github.io/your-repo/

## 📁 Project Structure
```
careerpath-ai/
├── backend/
│   ├── app.py                 # Main application entry point
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Container build instructions
│   └── .gcloudignore          # Cloud Run ignore patterns
└── frontend/
    └── index.html             # Static frontend (single file)
```
