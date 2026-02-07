import pandas as pd
from sqlalchemy.orm import Session

from accounting.models import RequestLog


class DatasetBuilder:


    def __init__(self, db: Session):
        self.db = db


    def _aggregate(self, records, freq: str):

        data = []

        for r in records:

            ts = r.created_at

            if freq == "daily":
                t = ts.date()

            elif freq == "hourly":
                t = ts.replace(
                    minute=0,
                    second=0,
                    microsecond=0
                )

            elif freq == "minute":
                t = ts.replace(
                    second=0,
                    microsecond=0
                )

            else:
                raise ValueError("Invalid frequency")

            data.append({
                "time": t,
                "tokens": r.total_tokens,
                "cost": r.cost_usd
            })

        df = pd.DataFrame(data)

        if df.empty:
            return df

        df = (
            df.groupby("time")
            .agg({
                "tokens": "sum",
                "cost": "sum"
            })
            .reset_index()
            .sort_values("time")
        )

        return df


    def build_usage(self):

        records = self.db.query(RequestLog).all()

        if not records:
            return pd.DataFrame(), "none"

        # Try daily
        daily = self._aggregate(records, "daily")

        if len(daily) >= 3:
            return daily, "daily"

        # Try hourly
        hourly = self._aggregate(records, "hourly")

        if len(hourly) >= 3:
            return hourly, "hourly"

        # Try minute
        minute = self._aggregate(records, "minute")

        if len(minute) >= 3:
            return minute, "minute"

        return pd.DataFrame(), "insufficient"
