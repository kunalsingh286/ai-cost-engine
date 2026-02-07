import re


class RequestClassifier:

    def __init__(self):
        pass


    def classify(self, prompt: str) -> str:

        length = len(prompt)

        code_keywords = [
            "python", "java", "c++", "sql", "algorithm",
            "function", "class", "debug", "error"
        ]

        technical = any(
            kw in prompt.lower()
            for kw in code_keywords
        )

        if technical:
            return "high"

        if length < 150:
            return "low"

        if length < 500:
            return "medium"

        return "high"
