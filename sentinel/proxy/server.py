"""
Sentinel Proxy server.
"""

from typing import Optional
import time

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

from sentinel.organism import Organism
from sentinel.proxy.config import ProxyConfig
from sentinel.proxy.dashboard import dashboard_html
from sentinel.proxy.middleware import SentinelMiddleware
from sentinel.proxy.openai_compat import ChatCompletionRequest
from sentinel.proxy.provider_clients import ProviderPool


def create_app(config: Optional[ProxyConfig] = None) -> FastAPI:
    config = config or ProxyConfig.from_env()
    organism = Organism(name="sentinel-proxy", autonomous=True, persist_path=config.persist_path)

    providers = ProviderPool()
    for provider_config in config.providers.values():
        providers.add_provider(provider_config)

    middleware = SentinelMiddleware(organism, config)

    app = FastAPI(
        title="Sentinel AI Proxy",
        description="Change one line. Your AI gets better and cheaper.",
        version="0.5.0",
    )

    @app.get("/")
    async def root():
        return {"status": "alive", "organism": organism.state, "pain": organism.pain}

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        return dashboard_html(organism)

    @app.get("/v1/models")
    async def list_models():
        models = []
        for provider_config in config.providers.values():
            for model in provider_config.models:
                models.append(
                    {
                        "id": model,
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": provider_config.name,
                    }
                )
        return {"object": "list", "data": models}

    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request):
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(status_code=400, content={"error": {"message": "Invalid JSON", "type": "invalid_request"}})

        chat_request = ChatCompletionRequest.from_dict(body)
        sentinel_quality = request.headers.get("x-sentinel-quality")
        if sentinel_quality:
            chat_request.sentinel_required_quality = float(sentinel_quality)
        sentinel_speed = request.headers.get("x-sentinel-prefer-speed")
        if sentinel_speed:
            chat_request.sentinel_prefer_speed = sentinel_speed.lower() == "true"

        chat_request, metadata = await middleware.process_request(chat_request)
        if metadata.get("blocked"):
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "message": f"Request blocked by Sentinel: {metadata.get('block_reason')}",
                        "type": "sentinel_blocked",
                    },
                    "sentinel": {"blocked": True, "reasons": metadata.get("block_reason", [])},
                },
            )

        if organism.tardigrade.is_hibernating:
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "message": "AI system is in safe mode (hibernating). Try again later.",
                        "type": "sentinel_hibernating",
                    }
                },
            )

        try:
            client = providers.get_client(chat_request.model)
            if not client:
                return JSONResponse(
                    status_code=500,
                    content={"error": {"message": f"No provider for model {chat_request.model}"}},
                )
            request_data = chat_request.to_openai_dict()
            request_data["stream"] = False
            response = await client.chat_completion(request_data, model=chat_request.model)
        except Exception as e:
            organism.observe("error_rate", 1.0)
            return JSONResponse(
                status_code=502,
                content={"error": {"message": f"Provider error: {str(e)}", "type": "provider_error"}},
            )

        response, _ = await middleware.process_response(response, chat_request, metadata)
        return JSONResponse(content=response)

    @app.get("/v1/sentinel/health")
    async def health():
        return organism.report()

    @app.get("/v1/sentinel/savings")
    async def savings():
        return organism.router.cost_report()

    @app.get("/v1/sentinel/experience")
    async def experience():
        return organism.experience.report()

    @app.get("/v1/sentinel/trust")
    async def trust():
        return organism.trust.report()

    @app.post("/v1/sentinel/feedback")
    async def feedback(request: Request):
        body = await request.json()
        exp_id = body.get("experience_id")
        outcome = body.get("outcome", 0.5)
        if exp_id:
            organism.experience.record_outcome(exp_id, outcome)
        return {"status": "recorded"}

    @app.on_event("shutdown")
    async def shutdown():
        organism.save()
        await providers.close_all()

    return app


def run(host: str = "0.0.0.0", port: int = 8741):
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run()
