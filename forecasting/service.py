from sqlalchemy.orm import Session

from forecasting.dataset import DatasetBuilder
from forecasting.model import ForecastModel
from forecasting.capacity import CapacityPlanner


class ForecastService:


    def __init__(self, db: Session):

        self.builder = DatasetBuilder(db)
        self.model = ForecastModel()
        self.capacity = CapacityPlanner()


    def generate(self, days: int = 7) -> dict:

        df, granularity = self.builder.build_usage()

        if df.empty:
            return {
                "status": "insufficient_data"
            }

        trained = self.model.fit(df)

        if not trained:
            return {
                "status": "training_failed"
            }

        token_forecast = self.model.predict_tokens(days)

        cost_forecast = self.model.predict_cost(token_forecast)

        capacity = self.capacity.estimate(
            sum(token_forecast) / days
        )

        return {
            "status": "ok",
            "granularity": granularity,
            "points_used": len(df),
            "days": days,
            "token_forecast": token_forecast,
            "cost_forecast": cost_forecast,
            "capacity": capacity
        }
