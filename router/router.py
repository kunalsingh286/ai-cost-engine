from router.classifier import RequestClassifier
from router.policy import RoutingPolicy


class ModelRouter:

    def __init__(self):

        self.classifier = RequestClassifier()
        self.policy = RoutingPolicy()


    def route(self, prompt: str) -> dict:

        tier = self.classifier.classify(prompt)

        model = self.policy.select_model(tier)

        return {
            "tier": tier,
            "model": model
        }
