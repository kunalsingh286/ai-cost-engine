from gateway.config import load_config


config = load_config()

PRICES = config["pricing"]


def calculate_cost(model: str, total_tokens: int) -> float:

    price_per_million = PRICES.get(model, 0.1)

    cost = (total_tokens / 1_000_000) * price_per_million

    return round(cost, 6)
