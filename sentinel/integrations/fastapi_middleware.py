"""
FastAPI middleware — every request flows through the organism.
"""

import time


class SentinelMiddleware:
    """ASGI middleware for FastAPI/Starlette."""

    def __init__(self, app, organism):
        self.app = app
        self.organism = organism

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.time()
        status_code = 200

        if self.organism.respiratory.current_mode == "emergency":
            response_body = b'{"error": "Service temporarily in safe mode"}'
            await send(
                {
                    "type": "http.response.start",
                    "status": 503,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send({"type": "http.response.body", "body": response_body})
            return

        if self.organism.tardigrade.is_hibernating:
            fallback = self.organism.tardigrade.respond()
            response_body = f'{{"status": "hibernating", "message": "{fallback}"}}'.encode()
            await send(
                {
                    "type": "http.response.start",
                    "status": 503,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send({"type": "http.response.body", "body": response_body})
            return

        original_send = send

        async def capture_send(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
            await original_send(message)

        try:
            await self.app(scope, receive, capture_send)
        except Exception:
            status_code = 500
            raise
        finally:
            latency = (time.time() - start) * 1000
            self.organism.observe("request_latency", latency)
            self.organism.observe("error_rate", 1.0 if status_code >= 500 else 0.0)
            self.organism.signal({"latency": latency, "status": status_code})
