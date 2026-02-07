from fastapi import FastAPI, HTTPException, Header, Depends, Query
from pydantic import BaseModel
from typing import Optional

from sqlalchemy.orm import Session

from gateway.ollama_client import OllamaClient
from gateway.config import load_config

from accounting.database import get_db
from accounting.tokenizer import count_tokens
from accounting.cost_engine import calculate_cost
from accounting.logger import log_request
from accounting.budget import BudgetManager

from router.router import ModelRouter

from forecasting.service import ForecastService


app = FastAPI(
    title="AI Cost Engine Gateway",
    version="0.5.0"
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
    budget_status: str


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

        budget = BudgetManager(db)

        user_budget = budget.check_user_budget(x_api_key)

        org_budget = budget.check_org_budget()

        status = min(
            user_budget["status"],
            org_budget["status"],
            key=lambda x: ["ok", "warning", "critical", "blocked"].index(x)
        )

        route_info = router_engine.route(request.prompt, status)

        if route_info["blocked"]:
            raise HTTPException(
                status_code=403,
                detail="Budget exceeded"
            )

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

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "model": model,
        "tier": tier,
        "response": response,
        "cost": cost,
        "tokens": total_tokens,
        "budget_status": status
    }


@app.get("/v1/forecast")
def forecast(
    days: int = Query(7, ge=3, le=30),
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):

    verify_key(x_api_key)

    service = ForecastService(db)

    result = service.generate(days)

    return result

# ------------------ Metrics ------------------

from prometheus_client import Counter, generate_latest


REQUEST_COUNT = Counter(
    "aicost_requests_total",
    "Total API requests"
)


@app.middleware("http")
async def metrics_middleware(request, call_next):

    REQUEST_COUNT.inc()

    response = await call_next(request)

    return response


@app.get("/metrics")
def metrics():

    return generate_latest()
