import json
import os

from flask import Flask, jsonify, render_template_string, request
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

app = Flask(__name__)

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

SYSTEM_INSTRUCTION = """You are a careful, warm AI assistant supporting elderly care.
You read daily activity logs and produce structured insights for caregivers and family.

Rules:
- Be specific and grounded in what the log actually says. Never invent details.
- Avoid alarm. Frame concerns calmly and constructively.
- Severity guidance:
    'low'    = monitor casually
    'medium' = mention to family/caregiver soon
    'high'   = warrants prompt attention from a healthcare professional
- If the log is too vague, say so in the summary and return empty arrays.
- This is decision support, not medical advice."""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "2-3 sentence plain-language summary of the day."
        },
        "behavior_pattern": {
            "type": "string",
            "description": "Notable patterns across sleep, meals, mood, activity, social contact."
        },
        "concerns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "issue": {"type": "string"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "suggested_action": {"type": "string"}
                },
                "required": ["issue", "severity", "suggested_action"]
            }
        },
        "positive_notes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Short bright-spot observations (e.g. 'ate dinner well')."
        }
    },
    "required": ["summary", "behavior_pattern", "concerns", "positive_notes"]
}

model = GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION,
)


@app.route("/", methods=["GET"])
def home():
    return render_template_string(INDEX_HTML)


@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok"


@app.route("/analyze", methods=["POST"])
def analyze():
    body = request.get_json(silent=True) or {}
    text = (body.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Field 'text' is required."}), 400
    if len(text) > 8000:
        return jsonify({"error": "Log too long (max 8000 characters)."}), 400

    try:
        response = model.generate_content(
            f"Analyze this daily activity log:\n\n{text}",
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                temperature=0.3,
            ),
        )
        return jsonify(json.loads(response.text))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quietude — Elderly Care Insights</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..500&family=Instrument+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --cream: #f6f1e8;
    --paper: #fbf7ee;
    --ink: #1f1a14;
    --ink-soft: #5a4f42;
    --sage: #5b6e54;
    --amber: #b8782b;
    --terra: #a3492c;
    --line: rgba(31,26,20,0.12);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { background: var(--cream); color: var(--ink); }
  body {
    font-family: 'Instrument Sans', system-ui, sans-serif;
    font-size: 16px;
    line-height: 1.5;
    min-height: 100vh;
    background-image:
      radial-gradient(circle at 15% 0%, rgba(184,120,43,0.09), transparent 45%),
      radial-gradient(circle at 90% 100%, rgba(91,110,84,0.09), transparent 45%);
  }
  .nameplate {
    border-bottom: 1px solid var(--line);
    padding: 18px 32px;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 12px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--ink-soft);
  }
  .nameplate strong {
    font-family: 'Fraunces', serif;
    font-weight: 400;
    font-style: italic;
    font-size: 24px;
    letter-spacing: -0.02em;
    text-transform: none;
    color: var(--ink);
  }
  main { max-width: 1180px; margin: 0 auto; padding: 64px 32px 96px; }
  .masthead { text-align: center; margin-bottom: 64px; }
  .masthead h1 {
    font-family: 'Fraunces', serif;
    font-weight: 350;
    font-size: clamp(40px, 6vw, 72px);
    line-height: 0.98;
    letter-spacing: -0.025em;
    margin-bottom: 18px;
  }
  .masthead h1 em { font-style: italic; font-weight: 300; }
  .masthead p {
    font-size: 15px; color: var(--ink-soft);
    max-width: 480px; margin: 0 auto; line-height: 1.55;
  }
  .grid {
    display: grid;
    grid-template-columns: 1fr 1.15fr;
    gap: 48px;
    align-items: start;
  }
  @media (max-width: 820px) {
    .grid { grid-template-columns: 1fr; gap: 32px; }
    main { padding: 40px 20px 64px; }
  }
  .panel-label {
    font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase;
    color: var(--ink-soft); margin-bottom: 14px;
    display: flex; align-items: center; gap: 10px;
  }
  .panel-label::before {
    content: ''; width: 24px; height: 1px; background: var(--ink-soft);
  }
  textarea {
    width: 100%; min-height: 340px;
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 2px; padding: 22px;
    font-family: 'Instrument Sans', system-ui, sans-serif;
    font-size: 15px; line-height: 1.65; color: var(--ink);
    resize: vertical;
    transition: border-color 0.2s, background 0.2s;
  }
  textarea:focus { outline: none; border-color: var(--ink); background: #fff; }
  textarea::placeholder { color: rgba(31,26,20,0.35); font-style: italic; }
  .controls { display: flex; gap: 12px; margin-top: 16px; align-items: center; }
  button {
    font-family: 'Instrument Sans', system-ui, sans-serif;
    cursor: pointer; border-radius: 2px; transition: all 0.2s;
  }
  button.primary {
    background: var(--ink); color: var(--cream); border: none;
    padding: 14px 28px; font-size: 14px; letter-spacing: 0.04em; font-weight: 500;
  }
  button.primary:hover { background: #2f2820; }
  button.primary:disabled { opacity: 0.5; cursor: wait; }
  button.ghost {
    background: transparent; border: 1px solid var(--line);
    color: var(--ink-soft); padding: 13px 18px; font-size: 13px;
  }
  button.ghost:hover { border-color: var(--ink); color: var(--ink); }

  .results {
    background: var(--paper);
    border: 1px solid var(--line);
    padding: 36px; border-radius: 2px; min-height: 380px;
  }
  .empty {
    color: var(--ink-soft); font-style: italic;
    font-family: 'Fraunces', serif; font-size: 19px;
    text-align: center; padding: 100px 20px; opacity: 0.7;
  }
  .loading { text-align: center; padding: 80px 20px; color: var(--ink-soft); }
  .loading .dots span {
    display: inline-block; width: 6px; height: 6px;
    background: var(--ink); border-radius: 50%;
    margin: 0 3px; animation: pulse 1.2s ease-in-out infinite;
  }
  .loading .dots span:nth-child(2) { animation-delay: 0.15s; }
  .loading .dots span:nth-child(3) { animation-delay: 0.3s; }
  .loading .label { margin-top: 18px; font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase; }
  @keyframes pulse {
    0%, 80%, 100% { opacity: 0.2; transform: translateY(0); }
    40% { opacity: 1; transform: translateY(-3px); }
  }

  .reading { animation: fadeIn 0.5s ease; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

  .summary {
    font-family: 'Fraunces', serif; font-weight: 350;
    font-size: 22px; line-height: 1.4; letter-spacing: -0.01em;
    border-left: 2px solid var(--ink); padding-left: 22px; margin-bottom: 32px;
  }
  .section { margin-bottom: 28px; }
  .section:last-child { margin-bottom: 0; }
  .section h3 {
    font-family: 'Instrument Sans', system-ui, sans-serif;
    font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase;
    color: var(--ink-soft); margin-bottom: 12px; font-weight: 600;
  }
  .pattern { font-size: 15px; line-height: 1.65; }

  .concern {
    border-top: 1px solid var(--line); padding: 16px 0;
    display: grid; grid-template-columns: auto 1fr; gap: 16px; align-items: start;
  }
  .concern:last-child { border-bottom: 1px solid var(--line); }
  .severity {
    font-size: 10px; letter-spacing: 0.16em; text-transform: uppercase;
    padding: 5px 10px; border-radius: 2px; font-weight: 600;
    white-space: nowrap; margin-top: 2px;
  }
  .severity.low    { background: rgba(91,110,84,0.16);  color: var(--sage); }
  .severity.medium { background: rgba(184,120,43,0.16); color: var(--amber); }
  .severity.high   { background: rgba(163,73,44,0.18);  color: var(--terra); }
  .concern .issue { font-weight: 500; margin-bottom: 4px; }
  .concern .action { font-size: 14px; color: var(--ink-soft); font-style: italic; }

  .positives { display: flex; flex-wrap: wrap; gap: 8px; }
  .chip {
    background: rgba(91,110,84,0.13); color: var(--sage);
    padding: 6px 12px; border-radius: 20px; font-size: 13px;
  }

  .error {
    color: var(--terra); background: rgba(163,73,44,0.08);
    padding: 16px; border-radius: 2px; font-size: 14px;
    border-left: 2px solid var(--terra);
  }

  footer {
    text-align: center; font-size: 11px;
    color: var(--ink-soft); padding: 28px;
    border-top: 1px solid var(--line);
    letter-spacing: 0.08em; text-transform: uppercase;
  }
</style>
</head>
<body>
  <header class="nameplate">
    <span>Vol. 01 — Daily Reading</span>
    <strong>Quietude</strong>
    <span>Elderly Care</span>
  </header>

  <main>
    <div class="masthead">
      <h1>A gentle <em>reading</em><br>of the day's quiet signals</h1>
      <p>Paste a daily activity log. Receive a calm, structured summary with notable patterns and any concerns worth a closer look.</p>
    </div>

    <div class="grid">
      <section>
        <div class="panel-label">The log</div>
        <textarea id="logInput" placeholder="Describe the day — meals, sleep, mood, walks, who they spoke with, anything unusual…"></textarea>
        <div class="controls">
          <button class="primary" id="analyzeBtn">Analyze</button>
          <button class="ghost" id="sampleBtn">Use sample</button>
        </div>
      </section>

      <section>
        <div class="panel-label">The reading</div>
        <div class="results" id="results">
          <div class="empty">Awaiting today's entry…</div>
        </div>
      </section>
    </div>
  </main>

  <footer>A prototype — not a medical device — for caregiver reference only</footer>

  <script>
    const SAMPLE = `Mrs. Tanaka woke at 7:30am. Ate half her breakfast — toast and tea, said she "wasn't very hungry." Took her morning walk for 15 minutes, noticeably slower than her usual 30. Napped 11am to 1pm. Skipped lunch entirely. Spent the afternoon watching TV, mostly quiet, didn't call her daughter as she usually does on Sundays. Ate dinner well at 6pm (rice, fish, vegetables). In bed by 9pm but woke twice in the night to use the bathroom. No falls, no medication missed.`;

    const $log = document.getElementById('logInput');
    const $btn = document.getElementById('analyzeBtn');
    const $sample = document.getElementById('sampleBtn');
    const $results = document.getElementById('results');

    $sample.addEventListener('click', () => { $log.value = SAMPLE; $log.focus(); });

    $btn.addEventListener('click', async () => {
      const text = $log.value.trim();
      if (!text) { $log.focus(); return; }

      $btn.disabled = true;
      $btn.textContent = 'Reading…';
      $results.innerHTML = `
        <div class="loading">
          <div class="dots"><span></span><span></span><span></span></div>
          <div class="label">Reading the day</div>
        </div>`;

      try {
        const res = await fetch('/analyze', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({text})
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Request failed');
        render(data);
      } catch (err) {
        $results.innerHTML = `<div class="error"><strong>Could not complete the reading.</strong><br>${escapeHtml(err.message)}</div>`;
      } finally {
        $btn.disabled = false;
        $btn.textContent = 'Analyze';
      }
    });

    function render(d) {
      const concerns = (d.concerns || []).map(c => `
        <div class="concern">
          <span class="severity ${c.severity}">${escapeHtml(c.severity)}</span>
          <div>
            <div class="issue">${escapeHtml(c.issue)}</div>
            <div class="action">${escapeHtml(c.suggested_action || '')}</div>
          </div>
        </div>
      `).join('');

      const positives = (d.positive_notes || []).map(p =>
        `<span class="chip">${escapeHtml(p)}</span>`
      ).join('');

      $results.innerHTML = `
        <div class="reading">
          <div class="summary">${escapeHtml(d.summary || '')}</div>
          <div class="section">
            <h3>Behavior pattern</h3>
            <div class="pattern">${escapeHtml(d.behavior_pattern || '')}</div>
          </div>
          ${concerns ? `<div class="section"><h3>Worth attention</h3>${concerns}</div>` : ''}
          ${positives ? `<div class="section"><h3>Bright spots</h3><div class="positives">${positives}</div></div>` : ''}
        </div>
      `;
    }

    function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, c => ({
        '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
      }[c]));
    }
  </script>
</body>
</html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
