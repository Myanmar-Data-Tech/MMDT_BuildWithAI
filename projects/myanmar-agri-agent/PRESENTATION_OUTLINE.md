# Project Title: ရွှေတောင်သူ အကြံပေး

*   **Event:** Google Developers Community - Build with AI MMDT 2026

## Key Features
*   **Multimodal Input:** Support for Burmese text and native voice recording.
*   **Voice History:** Ability to re-listen to voice queries directly in the chat.
*   **Action-Oriented AI:** Specialized system instructions ensure the AI provides actionable steps

## Tech Stack
*   **AI Engine:** Google Gemini 2.5 Flash (via Vertex AI)
*   **Security:** Application Default Credentials (ADC) for secure, keyless cloud authentication. (to avoid API key usage quota exauted error in Google AI Studio)
*   **Backend:** Python (FastAPI)
*   **Frontend:** Tailwind CSS, Lucide Icons, and Web Speech API.
*   **Cloud Infrastructure:** Google Cloud Run (Serverless) for effortless scaling and cost-efficiency.
*   **AI Coding:** Gemini CLI (Google Cloud Shell)
*   **Initial Prompt:** "i want to build a web app for Myanmar farmers, farmers can ask agent app via voice or text for agricultural issues. "ကုလားပဲ မြစ်ခြောက်ရောဂါကို ဘယ်လိုလုပ်ဖြေရှင်းရမလဲ" etc. app should give short and actionable advices. brain will be google gemini ai model 2.5 flash. app will be deoploy on google cloud run."

## How it Works
*   **Step 1:** User speaks or types in Burmese.
*   **Step 2:** Frontend captures audio/text; converts speech to text locally using Web Speech API.
*   **Step 3:** Backend sends the query to Gemini 2.5 Flash on Vertex AI with a specialized "Agricultural Expert" System Instruction.
*   **Step 4:** Gemini generates structured Markdown advice.
*   **Step 5:** UI renders the advice and keeps the original audio for user reference.

## Demo
*   **Live Demo Link:** https://myanmar-agri-agent-599279558972.us-central1.run.app
*   မြေပဲပင်တွင် ကျရောက်ဖျက်စီးသော ရွက်ထွင်းပိုး ကို ဘယ်လိုဖြေရှင်းရမလဲ?
*   ပြောင်းတွင်ကျရောက်သော ပျပိုးကို ဘယ်လို ကြိုကာကွယ်ရမလဲ?
