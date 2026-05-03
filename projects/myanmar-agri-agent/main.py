import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize Gemini Client with Application Default Credentials (ADC)
# When running on Google Cloud (Cloud Shell, Cloud Run), ADC is handled automatically.
client = genai.Client(
    vertexai=True,
    project="dotted-cat-495205-h1",
    location="us-central1"
)

SYSTEM_INSTRUCTION = """
You are a highly knowledgeable Myanmar agricultural expert assistant named "Farmer Buddy". 
Your goal is to provide practical, reliable, and actionable agricultural advice to Myanmar farmers in Burmese.

Guidelines for your responses:
1. Language: Always respond in clear, natural Burmese (Unicode).
2. Structure: 
   - Briefly acknowledge the issue.
   - Provide 3-5 clear, numbered actionable steps or solutions.
   - Keep the advice practical and low-cost where possible.
3. Actionability: Every piece of advice must be something a farmer can actually DO (e.g., specific water management, natural pest control, or soil treatment).
4. Brevity: Keep responses concise and easy to read on a mobile screen. Avoid long paragraphs.
5. Safety: If you suggest any pesticides or fertilizers, remind them to wear protective gear and follow label instructions.
6. Professionalism: If a problem is very complex, suggest visiting the nearest Department of Agriculture office.
"""

class ChatRequest(BaseModel):
    message: Optional[str] = None
    audio_base64: Optional[str] = None

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Use message if provided, otherwise default to a voice query indicator
        user_query = request.message if request.message else "အသံဖြင့် မေးမြန်းချက် (Voice query)"
        print(f"Received query: {user_query}")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
            ),
            contents=[user_query]
        )
        
        # Check if we have text in the response
        if response.text:
            reply = response.text
            print(f"Gemini Reply: {reply}")
        else:
            # Handle cases where response might be blocked or empty
            print(f"No text in response. Finish reason: {response.candidates[0].finish_reason}")
            reply = "တောင်းပန်ပါတယ်။ အကြံပြုချက်အပြည့်အစုံကို မဖော်ပြနိုင်ဖြစ်နေပါတယ်။ ခေတ္တစောင့်ပြီး ထပ်မေးပေးပါ။"
            
        return {"reply": reply}
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Detailed Error: {e}")
        return {"reply": "တောင်းပန်ပါတယ်။ တစ်ခုခုမှားယွင်းနေလို့ ခဏနေမှ ထပ်ကြိုးစားပေးပါ။"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
