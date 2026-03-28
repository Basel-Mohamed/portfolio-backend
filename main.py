from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 1. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    # Allow local development and your exact live domain
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. HEALTH CHECK ENDPOINT
# ==========================================
@app.get("/")
async def health_check():
    """
    Simple health check endpoint for Google Cloud Run and monitoring tools.
    """
    return {"status": "healthy", "service": "portfolio-api"}

# ==========================================
# 3. CHAT API ENDPOINT
# ==========================================
@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message")
    chat_history = data.get("chat_history", [])
    preamble = data.get("preamble", "")
    temperature = data.get("temperature", 0.3)

    api_key = os.environ.get("COHERE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured.")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.cohere.com/v1/chat",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "message": message,
                    "model": "command-r7b-12-2024",
                    "preamble": preamble,
                    "temperature": temperature,
                    "chat_history": chat_history
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))