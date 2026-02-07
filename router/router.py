from router.classifier import RequestClassifier
from router.policy import RoutingPolicy


class ModelRouter:


    def __init__(self):

        self.classifier = RequestClassifier()
        self.policy = RoutingPolicy()


    def route(self, prompt: str, budget_status: str) -> dict:

        base_tier = self.classifier.classify(prompt)

        final_tier = self.policy.enforce_budget(
            base_tier,
            budget_status
        )

        if final_tier == "blocked":
            return {
                "blocked": True
            }

        model = self.policy.select_model(final_tier)

        return {
            "blocked": False,
            "tier": final_tier,
            "model": model
        }
