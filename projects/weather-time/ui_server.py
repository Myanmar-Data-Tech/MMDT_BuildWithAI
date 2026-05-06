
from dotenv import load_dotenv
load_dotenv()

import uvicorn
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from google.adk.runners import InMemoryRunner
from google.genai import types
from agent import root_agent

app = FastAPI()
runner = InMemoryRunner(agent=root_agent)
if hasattr(runner, "auto_create_session"):
    runner.auto_create_session = True

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather & Time Agent UI</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 h-screen flex flex-col font-sans">
    <header class="bg-indigo-600 text-white py-4 px-6 shadow-lg">
        <h1 class="text-2xl font-bold">Weather & Time Agent</h1>
        <p class="text-indigo-100 text-sm">Ask about weather or time all over the world</p>
    </header>

    <main class="flex-1 overflow-y-auto p-6 space-y-4" id="chat-box">
        <div class="flex justify-start">
            <div class="bg-indigo-100 text-slate-800 px-4 py-2 rounded-2xl rounded-tl-none shadow-sm max-w-[80%]">
                Hello! I can help you with the weather or current time in New York or Tokyo. How can I assist you today?
            </div>
        </div>
    </main>

    <footer class="bg-white border-t p-4">
        <div class="max-w-4xl mx-auto flex gap-2">
            <input type="text" id="user-input" autofocus
                class="flex-1 min-w-0 border border-slate-300 rounded-full px-5 py-3 text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" 
                placeholder="What's the weather in New York?"
                autocomplete="off">
            <button id="send-btn" 
                class="bg-indigo-600 text-white rounded-full p-3 hover:bg-indigo-700 active:scale-95 transition-all shadow-md">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
            </button>
        </div>
    </footer>

    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');

        function appendMessage(role, text) {
            const wrapper = document.createElement('div');
            wrapper.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
            
            const msg = document.createElement('div');
            msg.className = `px-4 py-2 rounded-2xl shadow-sm max-w-[80%] ${
                role === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-none' 
                : 'bg-indigo-100 text-slate-800 rounded-tl-none'
            }`;
            msg.innerText = text;
            
            wrapper.appendChild(msg);
            chatBox.appendChild(wrapper);
            chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
        }

        function toggleTyping(show) {
            const id = 'typing-indicator';
            const existing = document.getElementById(id);
            if (show && !existing) {
                const wrapper = document.createElement('div');
                wrapper.id = id;
                wrapper.className = 'flex justify-start';
                wrapper.innerHTML = `
                    <div class="bg-indigo-100 text-slate-500 px-4 py-2 rounded-2xl rounded-tl-none shadow-sm flex gap-1 items-center">
                        <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                        <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                        <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
                    </div>
                `;
                chatBox.appendChild(wrapper);
                chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
            } else if (!show && existing) {
                existing.remove();
            }
        }

        let sessionId = null;

        async function send() {
            const query = userInput.value.trim();
            if (!query) return;
            appendMessage('user', query);
            userInput.value = '';
            toggleTyping(true);

            try {
                const reqBody = { query };
                if (sessionId) {
                    reqBody.session_id = sessionId;
                }
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(reqBody)
                });
                const data = await res.json();
                sessionId = data.session_id;
                toggleTyping(false);
                appendMessage('agent', data.response);
            } catch {
                toggleTyping(false);
                appendMessage('agent', 'Sorry, I encountered an error connecting to the agent.');
            }
        }

        sendBtn.onclick = send;
        userInput.onkeydown = (e) => {
            if (e.key === 'Enter') send();
        };
        // Ensure focus on load
        window.onload = () => userInput.focus();
    </script>
</body>
</html>
    """

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("query", "")
    session_id = data.get("session_id", str(uuid.uuid4()))

    final_response = ""
    # Use run_async to iterate through agent events
    async for event in runner.run_async(
        user_id="u_123",
        session_id=session_id,
        new_message=types.Content(parts=[types.Part(text=query)])
    ):
        if event.is_final_response() and event.content:
            # Concatenate response parts
            final_response = "".join(p.text for p in event.content.parts if p.text)

    return {"response": final_response or "The agent did not provide a text response.", "session_id": session_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)