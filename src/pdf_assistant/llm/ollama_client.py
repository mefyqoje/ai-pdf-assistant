import json
from collections.abc import Iterator

import requests


class OllamaClient:
    def __init__(
        self,
        model_name: str = "llama3.2:3b",
        base_url: str = "http://localhost:11434",
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
            },
            timeout=600,
        )

        response.raise_for_status()

        data = response.json()

        return str(data.get("response", "")).strip()

    def generate_stream(
        self,
        prompt: str,
    ) -> Iterator[str]:
        with requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
            },
            stream=True,
            timeout=600,
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                payload = json.loads(
                    line.decode("utf-8")
                )

                token = payload.get("response", "")

                if token:
                    yield token

                if payload.get("done"):
                    break