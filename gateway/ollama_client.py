import requests


class OllamaClient:

    def __init__(self, host="http://localhost:11434"):
        self.host = host


    def generate(self, model: str, prompt: str) -> str:

        url = f"{self.host}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=300)

        response.raise_for_status()

        data = response.json()

        return data.get("response", "")
