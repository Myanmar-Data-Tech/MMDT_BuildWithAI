# Certificate Study Plan Adviser

This project is a web-based **career certification adviser** that uses Google’s Agent Development Kit (ADK) and Gemini models to route questions to specialist agents (AI, cloud, or security), generate evidence-backed roadmaps with Google Search, and append a structured **3-month study plan** tied to the primary certification highlighted in the roadmap. The stack pairs a small Flask API with a static HTML front end for submitting queries and viewing Markdown-formatted answers.

---

## Installation

Prerequisites: **Python 3.11+** (matches the included `Dockerfile`) and a **Google AI / Vertex** setup as described under [Configuration](#configuration).

Dependencies are declared in [`parent_folder/requirements.txt`](parent_folder/requirements.txt).

1. **Clone or open this repository** and go to the folder that contains the dependency file:

   ```bash
   cd parent_folder
   ```

2. **Create and activate a virtual environment** (recommended):

   ```bash
   python -m venv .venv

   # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install Python packages**:

   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

4. **Configure environment variables** — create a `.env` file inside [`parent_folder/multi_tool_agent/`](parent_folder/multi_tool_agent/) (the app loads it from that directory). At minimum you need either a **Gemini API key** or **Vertex AI** settings:

   | Mode | Variables |
   |------|-----------|
   | **Gemini API** (AI Studio) | `GOOGLE_API_KEY` |
   | **Vertex AI** | `GOOGLE_GENAI_USE_VERTEXAI=TRUE`, plus `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` |

   Optional: strip quotes from the API key value if you wrapped it in quotes in `.env`.

There is **no** `package.json` in this repository; the UI uses CDN scripts only.

---

## Usage

The Flask app serves the UI from the **current working directory** (it uses `send_from_directory('.', 'index.html')`), so start the server from the `multi_tool_agent` package directory so `index.html` resolves correctly.

**Development (recommended):**

```bash
cd parent_folder/multi_tool_agent
python agent.py
```

Then open **http://localhost:5000** in a browser, enter a career or certification question, and use **Generate My Plan**. The front end POSTs JSON to `/query` and renders the returned Markdown.

**Run as a module** (same working-directory rule applies for static files):

```bash
cd parent_folder/multi_tool_agent
python -m agent
```

**Production-style server** (from `parent_folder`, matching the Docker layout):

```bash
cd parent_folder
gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 multi_tool_agent.agent:app
```

**Docker** (build context should be `parent_folder` where `Dockerfile` and `requirements.txt` live):

```bash
cd parent_folder
docker build -t certificate-adviser .
docker run -p 8080:8080 --env-file path/to/your.env certificate-adviser
```

The container sets `PORT=8080` and starts Gunicorn with `multi_tool_agent.agent:app`.

---

## Project structure

```text
certificate-study-plan-adviser/
├── README.md
└── parent_folder/
    ├── Dockerfile
    ├── requirements.txt
    └── multi_tool_agent/
        ├── __init__.py
        ├── agent.py       # ADK agents, routing, Flask API, app entry
        └── index.html     # Static UI (Tailwind + marked.js)
```

*(Add your own `.env` under `multi_tool_agent/` locally; do not commit secrets.)*

---

## Core logic (overview)

1. **Router agent** — A Gemini ADK agent classifies the user message and returns the name of one worker: `ai_certification_agent`, `cloud_certification_agent`, or `security_certification_agent`.
2. **Worker agent** — The chosen specialist (with **Google Search**) produces a certification roadmap in Markdown.
3. **Study plan** — The server uses a regular expression to pick the first Markdown bold span (text between double asterisks) in the roadmap as the target certification name (or a fallback label), then asks the same worker for a **3-month** month-by-month study plan in the same session.
4. **API** — `POST /query` accepts `{"query": "..."}` and returns `{"answer": "<markdown>"}`. `GET /` serves the HTML shell.

Additional agents (for example `certification_path_agent`) are defined for broader roadmap work; the interactive path above follows the router plus the three domain specialists.

---

## Tech stack

| Area | Libraries / tools |
|------|-------------------|
| **Language** | Python 3.11 |
| **Web** | [Flask](https://flask.palletsprojects.com/), [Flask-CORS](https://flask-cors.readthedocs.io/), [Gunicorn](https://gunicorn.org/) |
| **Google AI** | [google-adk](https://google.github.io/adk-docs/) (ADK agents, `Runner`, `InMemorySessionService`, `google_search` tool), [google-generativeai](https://github.com/google-gemini/generative-ai-python), [google-genai](https://github.com/googleapis/python-genai) |
| **Config** | [python-dotenv](https://github.com/theskumar/python-dotenv) |
| **Front end** | Static HTML, [Tailwind CSS](https://tailwindcss.com/) (CDN), [marked](https://marked.js.org/) (CDN) for Markdown rendering |
| **Containers** | Docker (`python:3.11-slim` base image) |

---

## License

Add a `LICENSE` file to this repository if you intend to distribute or open-source the project.
