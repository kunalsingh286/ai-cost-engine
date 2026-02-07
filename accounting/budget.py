from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

from accounting.models import RequestLog
from gateway.config import load_config


config = load_config()

USER_DAILY_LIMIT = config["budgets"]["user_daily"]
ORG_MONTHLY_LIMIT = config["budgets"]["org_monthly"]


class BudgetManager:


    def __init__(self, db: Session):
        self.db = db


    def get_user_daily_spend(self, user_key: str) -> float:

        today = datetime.utcnow().date()

        total = (
            self.db.query(func.sum(RequestLog.cost_usd))
            .filter(RequestLog.user_key == user_key)
            .filter(RequestLog.created_at >= today)
            .scalar()
        )

        return float(total or 0.0)


    def get_org_monthly_spend(self) -> float:

        start = datetime.utcnow().replace(day=1)

        total = (
            self.db.query(func.sum(RequestLog.cost_usd))
            .filter(RequestLog.created_at >= start)
            .scalar()
        )

        return float(total or 0.0)


    def check_user_budget(self, user_key: str) -> dict:

        spent = self.get_user_daily_spend(user_key)

        remaining = USER_DAILY_LIMIT - spent

        status = "ok"

        if remaining <= 0:
            status = "blocked"

        elif remaining <= 0.2 * USER_DAILY_LIMIT:
            status = "critical"

        elif remaining <= 0.5 * USER_DAILY_LIMIT:
            status = "warning"

        return {
            "spent": spent,
            "remaining": max(0.0, remaining),
            "status": status
        }


    def check_org_budget(self) -> dict:

        spent = self.get_org_monthly_spend()

        remaining = ORG_MONTHLY_LIMIT - spent

        status = "ok"

        if remaining <= 0:
            status = "blocked"

        elif remaining <= 0.2 * ORG_MONTHLY_LIMIT:
            status = "critical"

        elif remaining <= 0.5 * ORG_MONTHLY_LIMIT:
            status = "warning"

        return {
            "spent": spent,
            "remaining": max(0.0, remaining),
            "status": status
        }
