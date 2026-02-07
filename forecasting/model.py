import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class ForecastModel:


    def __init__(self):
        self.lr = LinearRegression()


    def fit(self, df: pd.DataFrame):

        if len(df) < 3:
            return False

        X = np.arange(len(df)).reshape(-1, 1)

        y_tokens = df["tokens"].values
        y_cost = df["cost"].values

        self.lr.fit(X, y_tokens)

        self.cost_mean = y_cost.mean()

        return True


    def predict_tokens(self, days: int) -> list:

        X_future = np.arange(
            len(range(days)),
            len(range(days)) + days
        ).reshape(-1, 1)

        preds = self.lr.predict(X_future)

        preds = np.maximum(preds, 0)

        return preds.tolist()


    def predict_cost(self, token_forecast: list) -> list:

        return [
            round((t / 1_000_000) * self.cost_mean, 6)
            for t in token_forecast
        ]
