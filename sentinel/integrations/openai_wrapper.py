"""
OpenAI Client Wrapper — drop-in replacement with built-in organism.
"""

import time

from ..core.event_bus import Event


class SentinelOpenAI:
    """Wrapper around OpenAI client that instruments with Sentinel."""

    def __init__(self, organism, api_key: str = None):
        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=api_key) if api_key else OpenAI()
        except ImportError as exc:
            raise ImportError("pip install openai") from exc

        self.organism = organism
        self.chat = self._ChatNamespace(self)

    class _ChatNamespace:
        def __init__(self, wrapper):
            self._wrapper = wrapper
            self.completions = self._CompletionsNamespace(wrapper)

        class _CompletionsNamespace:
            def __init__(self, wrapper):
                self._wrapper = wrapper

            def create(self, **kwargs):
                org = self._wrapper.organism
                messages = kwargs.get("messages", [])
                for msg in messages:
                    if msg.get("role") == "user":
                        check = org.process_input(msg.get("content", ""))
                        if not check.get("safe"):
                            org.bus.emit(
                                Event(
                                    type="openai.blocked",
                                    source="openai_wrapper",
                                    data={"threats": check.get("threats", [])},
                                    severity=3,
                                )
                            )
                            raise ValueError("Request blocked by Sentinel Skin")

                budget = org.respiratory.budget
                if budget < 0.3 and str(kwargs.get("model", "")).startswith("gpt-4"):
                    kwargs["model"] = "gpt-4o-mini"

                if "temperature" not in kwargs:
                    kwargs["temperature"] = org.endocrine.get("creativity")

                start = time.time()
                try:
                    response = self._wrapper._client.chat.completions.create(**kwargs)
                    latency = (time.time() - start) * 1000
                    org.observe("latency", latency)
                    if getattr(response, "usage", None):
                        org.observe("tokens_used", response.usage.total_tokens)
                    if getattr(response, "choices", None):
                        content = response.choices[0].message.content or ""
                        org.observe("response_length", len(content))
                        org.process_output(content)
                    org.observe("error_rate", 0.0)
                    return response
                except Exception:
                    latency = (time.time() - start) * 1000
                    org.observe("latency", latency)
                    org.observe("error_rate", 1.0)
                    raise
