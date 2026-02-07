from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from gateway.ollama_client import OllamaClient
from gateway.config import load_config


app = FastAPI(
    title="AI Cost Engine Gateway",
    version="0.1.0"
)


config = load_config()

ollama = OllamaClient()


class ChatRequest(BaseModel):
    prompt: str
    model: Optional[str] = None


class ChatResponse(BaseModel):
    model: str
    response: str


API_KEYS = {
    "dev-key-123"
}


def verify_key(key: Optional[str]):

    if key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/models")
def list_models():

    models = (
        config["models"]["high"]
        + config["models"]["medium"]
        + config["models"]["low"]
    )

    return {"models": models}


@app.post("/v1/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    x_api_key: Optional[str] = Header(None)
):

    verify_key(x_api_key)

    model = request.model

    if not model:
        model = config["models"]["medium"][0]

    try:
        result = ollama.generate(model, request.prompt)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "model": model,
        "response": result
    }
