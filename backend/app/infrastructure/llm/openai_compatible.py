import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.infrastructure.llm.gateway import LlmGatewayUnavailable, LlmGeneration
from app.infrastructure.llm.prompt import (
    BASE_SYSTEM_PROMPT,
    FALLBACK_ANSWER,
    render_user_prompt,
)
from app.infrastructure.rag.simple_retriever import RetrievalResult


class OpenAICompatibleGateway:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 20.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate(self, question: str, contexts: list[RetrievalResult]) -> LlmGeneration:
        prompt = render_user_prompt(question, contexts)
        if not contexts:
            return LlmGeneration(
                answer=FALLBACK_ANSWER,
                safe_to_answer=False,
                prompt=prompt,
                provider="openai-compatible",
            )

        response = self._request_chat_completion(prompt)
        answer = response.strip()
        safe_to_answer = bool(answer) and answer != FALLBACK_ANSWER
        return LlmGeneration(
            answer=answer or FALLBACK_ANSWER,
            safe_to_answer=safe_to_answer,
            prompt=prompt,
            provider="openai-compatible",
        )

    def _request_chat_completion(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "temperature": 0.0,
            "messages": [
                {"role": "system", "content": BASE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        request = Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            raise LlmGatewayUnavailable(f"LLM returned {exc.code}: {error_body}") from exc
        except URLError as exc:
            raise LlmGatewayUnavailable(f"LLM unavailable: {exc.reason}") from exc

        data = json.loads(body)
        choices = data.get("choices", [])
        if not choices:
            raise LlmGatewayUnavailable("LLM response did not include choices.")

        message = choices[0].get("message", {})
        return str(message.get("content", ""))
