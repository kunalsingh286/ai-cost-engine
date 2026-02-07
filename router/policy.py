from gateway.config import load_config


config = load_config()


class RoutingPolicy:

    def __init__(self):
        self.models = config["models"]


    def get_models_for_tier(self, tier: str):

        return self.models.get(tier, [])


    def downgrade(self, tier: str):

        if tier == "high":
            return "medium"

        if tier == "medium":
            return "low"

        return "low"


    def select_model(self, tier: str):

        models = self.get_models_for_tier(tier)

        if models:
            return models[0]

        downgraded = self.downgrade(tier)

        models = self.get_models_for_tier(downgraded)

        if models:
            return models[0]

        raise RuntimeError("No available models")
