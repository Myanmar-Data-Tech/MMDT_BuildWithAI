# Elderly AI — *Quietude*

A gentle Flask web app that reads daily activity logs for elderly people and returns a calm, structured "reading" of the day — surfacing patterns, concerns, and bright spots — to support caregivers and family.

> ⚠️ **Disclaimer:** This is a prototype for caregiver reference only. It is **not** a medical device and does not provide medical advice.

---

## ✨ Features

- **Plain-language summary** — 2-3 sentence overview of the day
- **Behavior pattern detection** — sleep, meals, mood, activity, social contact
- **Severity-tagged concerns** — `low` / `medium` / `high` with suggested actions
- **Positive notes** — bright spots from the day
- **Calm, editorial UI** — typography-first design (Fraunces + Instrument Sans)
- **Structured JSON output** — enforced via Vertex AI response schema

---

## 🛠 Tech Stack

| Layer       | Choice                                      |
|-------------|---------------------------------------------|
| Backend     | Flask (Python 3.10+)                        |
| Production  | Gunicorn (WSGI server)                      |
| AI Model    | Gemini 2.5 Flash (via Vertex AI)            |
| Frontend    | Vanilla HTML/CSS/JS (single-page, no build) |
| Hosting     | Google Cloud Run (recommended)              |

---

## ☁️ GCP Project

- **Project ID:** `adk-multi-agent-mtk`
- **Region:** `us-central1`

### Required APIs
Enable these in your GCP project:
- `aiplatform.googleapis.com` (Vertex AI)
- `run.googleapis.com` (Cloud Run, if deploying)

```bash
gcloud services enable aiplatform.googleapis.com run.googleapis.com \
  --project=adk-multi-agent-mtk
```

---

## 📁 Project Structure

```
elderly-ai/
├── README.md           # This file
├── app.py              # Flask app + embedded HTML/JS UI
└── requirements.txt    # Python dependencies
```

---

## 🔌 API Reference

### `GET /`
Renders the *Quietude* UI — paste a log, click **Analyze**.

### `GET /healthz`
Health check. Returns `200 ok`.

### `POST /analyze`

**Request body:**
```json
{ "text": "Mrs. Tanaka woke at 7:30am. Ate half her breakfast..." }
```

**Constraints:**
- `text` is required
- Max length: **8000 characters**

**Response (200):**
```json
{
  "summary": "A quieter day than usual...",
  "behavior_pattern": "Reduced appetite at breakfast and lunch...",
  "concerns": [
    {
      "issue": "Skipped lunch and ate only half of breakfast",
      "severity": "medium",
      "suggested_action": "Mention to family; check if appetite returns tomorrow."
    }
  ],
  "positive_notes": ["Ate dinner well", "No falls or missed medication"]
}
```

**Severity scale:**
- `low` — monitor casually
- `medium` — mention to family/caregiver soon
- `high` — warrants prompt attention from a healthcare professional

**Error response (400 / 500):**
```json
{ "error": "Field 'text' is required." }
```

---

## 🚀 Setup

### 1. Clone & navigate
```bash
cd projects/elderly-ai
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Authenticate with GCP
```bash
gcloud auth application-default login
gcloud config set project adk-multi-agent-mtk
```

### 5. Set environment variables
```bash
export GOOGLE_CLOUD_PROJECT=adk-multi-agent-mtk
export GOOGLE_CLOUD_LOCATION=us-central1
```

### 6. Run locally

**Development:**
```bash
python app.py
```

**Production-style (Gunicorn):**
```bash
gunicorn -b 0.0.0.0:8080 app:app
```

Open **http://localhost:8080** — click **Use sample** to try it.

---

## ☁️ Deploy to Cloud Run

```bash
gcloud run deploy elderly-ai \
  --source . \
  --region us-central1 \
  --project adk-multi-agent-mtk \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=adk-multi-agent-mtk,GOOGLE_CLOUD_LOCATION=us-central1
```

Cloud Run will auto-detect the Python app, build a container, and deploy it.

---

## 🔐 Environment Variables

| Variable                  | Required | Default       | Description                      |
|---------------------------|----------|---------------|----------------------------------|
| `GOOGLE_CLOUD_PROJECT`    | ✅       | —             | Your GCP project ID              |
| `GOOGLE_CLOUD_LOCATION`   | ❌       | `us-central1` | Vertex AI region                 |
| `PORT`                    | ❌       | `8080`        | Port for local dev (Flask `app.run`) |

---

## 📦 Dependencies

| Package                    | Purpose                                |
|----------------------------|----------------------------------------|
| `flask`                    | Web framework                          |
| `gunicorn`                 | Production WSGI server                 |
| `google-cloud-aiplatform`  | Vertex AI SDK (provides `vertexai`)    |

---

## 🧪 Try it

After running locally, try the sample log:

> Mrs. Tanaka woke at 7:30am. Ate half her breakfast — toast and tea, said she "wasn't very hungry." Took her morning walk for 15 minutes, noticeably slower than her usual 30. Napped 11am to 1pm. Skipped lunch entirely...

Or via curl:
```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Slept poorly. Ate breakfast. Walked 10 min. No calls today."}'
```

---

## 🪪 License

Prototype built for the **MMDT BuildWithAI Workshop**.
