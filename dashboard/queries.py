import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

from accounting.models import RequestLog


class AnalyticsService:


    def __init__(self, db: Session):
        self.db = db


    def cost_over_time(self):

        rows = (
            self.db.query(
                func.date(RequestLog.created_at),
                func.sum(RequestLog.cost_usd)
            )
            .group_by(func.date(RequestLog.created_at))
            .order_by(func.date(RequestLog.created_at))
            .all()
        )

        df = pd.DataFrame(
            rows,
            columns=["date", "cost"]
        )

        return df


    def tokens_over_time(self):

        rows = (
            self.db.query(
                func.date(RequestLog.created_at),
                func.sum(RequestLog.total_tokens)
            )
            .group_by(func.date(RequestLog.created_at))
            .order_by(func.date(RequestLog.created_at))
            .all()
        )

        df = pd.DataFrame(
            rows,
            columns=["date", "tokens"]
        )

        return df


    def cost_by_model(self):

        rows = (
            self.db.query(
                RequestLog.model,
                func.sum(RequestLog.cost_usd)
            )
            .group_by(RequestLog.model)
            .all()
        )

        df = pd.DataFrame(
            rows,
            columns=["model", "cost"]
        )

        return df


    def top_users(self, limit: int = 5):

        rows = (
            self.db.query(
                RequestLog.user_key,
                func.sum(RequestLog.cost_usd).label("cost")
            )
            .group_by(RequestLog.user_key)
            .order_by(func.sum(RequestLog.cost_usd).desc())
            .limit(limit)
            .all()
        )

        df = pd.DataFrame(
            rows,
            columns=["user", "cost"]
        )

        return df
