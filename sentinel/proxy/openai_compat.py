"""
OpenAI API compatibility layer.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time


@dataclass
class ChatMessage:
    role: str
    content: str
    name: Optional[str] = None
    tool_calls: Optional[list] = None
    tool_call_id: Optional[str] = None


@dataclass
class ChatCompletionRequest:
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    tools: Optional[list] = None
    tool_choice: Optional[Any] = None
    response_format: Optional[dict] = None
    seed: Optional[int] = None
    stop: Optional[Any] = None
    presence_penalty: float = 0
    frequency_penalty: float = 0
    user: Optional[str] = None
    sentinel_required_quality: Optional[float] = None
    sentinel_max_cost: Optional[float] = None
    sentinel_prefer_speed: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "ChatCompletionRequest":
        messages = [
            ChatMessage(
                role=m.get("role", "user"),
                content=m.get("content", ""),
                name=m.get("name"),
                tool_calls=m.get("tool_calls"),
                tool_call_id=m.get("tool_call_id"),
            )
            for m in data.get("messages", [])
        ]
        return cls(
            model=data.get("model", "gpt-4o"),
            messages=messages,
            temperature=data.get("temperature"),
            top_p=data.get("top_p"),
            max_tokens=data.get("max_tokens"),
            stream=data.get("stream", False),
            tools=data.get("tools"),
            tool_choice=data.get("tool_choice"),
            response_format=data.get("response_format"),
            seed=data.get("seed"),
            stop=data.get("stop"),
            presence_penalty=data.get("presence_penalty", 0),
            frequency_penalty=data.get("frequency_penalty", 0),
            user=data.get("user"),
            sentinel_required_quality=data.get("sentinel_required_quality"),
            sentinel_max_cost=data.get("sentinel_max_cost"),
            sentinel_prefer_speed=data.get("sentinel_prefer_speed", False),
        )

    def to_openai_dict(self) -> dict:
        payload = {
            "model": self.model,
            "messages": [
                {
                    k: v
                    for k, v in {
                        "role": m.role,
                        "content": m.content,
                        "name": m.name,
                        "tool_calls": m.tool_calls,
                        "tool_call_id": m.tool_call_id,
                    }.items()
                    if v is not None
                }
                for m in self.messages
            ],
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.top_p is not None:
            payload["top_p"] = self.top_p
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        if self.stream:
            payload["stream"] = True
        if self.tools:
            payload["tools"] = self.tools
        if self.tool_choice is not None:
            payload["tool_choice"] = self.tool_choice
        if self.response_format:
            payload["response_format"] = self.response_format
        if self.seed is not None:
            payload["seed"] = self.seed
        if self.stop:
            payload["stop"] = self.stop
        if self.presence_penalty:
            payload["presence_penalty"] = self.presence_penalty
        if self.frequency_penalty:
            payload["frequency_penalty"] = self.frequency_penalty
        if self.user:
            payload["user"] = self.user
        return payload

    @property
    def user_message(self) -> str:
        for message in reversed(self.messages):
            if message.role == "user" and message.content:
                return message.content
        return ""

    @property
    def system_prompt(self) -> Optional[str]:
        for message in self.messages:
            if message.role == "system":
                return message.content
        return None

    @property
    def estimated_input_tokens(self) -> int:
        total_chars = sum(len(m.content or "") for m in self.messages)
        return max(1, total_chars // 4)


def format_openai_response(
    content: str,
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    finish_reason: str = "stop",
    sentinel_meta: dict = None,
) -> dict:
    response = {
        "id": f"sentinel-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
    }
    if sentinel_meta:
        response["sentinel"] = sentinel_meta
    return response
