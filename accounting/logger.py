from sqlalchemy.orm import Session

from accounting.models import RequestLog


def log_request(
    db: Session,
    user_key: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    cost: float
):

    total = prompt_tokens + completion_tokens

    record = RequestLog(
        user_key=user_key,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total,
        cost_usd=cost
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record
