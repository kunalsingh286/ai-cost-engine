from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional

from sqlalchemy.orm import Session

from gateway.ollama_client import OllamaClient
from gateway.config import load_config

from accounting.database import get_db
from accounting.tokenizer import count_tokens
from accounting.cost_engine import calculate_cost
from accounting.logger import log_request

from router.router import ModelRouter


app = FastAPI(
    title="AI Cost Engine Gateway",
    version="0.3.0"
)


config = load_config()

ollama = OllamaClient()

router_engine = ModelRouter()


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    model: str
    tier: str
    response: str
    cost: float
    tokens: int


API_KEYS = {
    "dev-key-123"
}


def verify_key(key: Optional[str]):

    if key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/v1/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):

    verify_key(x_api_key)

    try:

        route_info = router_engine.route(request.prompt)

        model = route_info["model"]
        tier = route_info["tier"]

        response = ollama.generate(model, request.prompt)

        prompt_tokens = count_tokens(request.prompt, model)

        completion_tokens = count_tokens(response, model)

        total_tokens = prompt_tokens + completion_tokens

        cost = calculate_cost(model, total_tokens)

        log_request(
            db=db,
            user_key=x_api_key,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "model": model,
        "tier": tier,
        "response": response,
        "cost": cost,
        "tokens": total_tokens
    }
