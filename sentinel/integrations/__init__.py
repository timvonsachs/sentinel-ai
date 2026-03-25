"""
Integrations — Drop-in connections to popular AI frameworks.
"""


def get_langchain_callback():
    from .langchain import SentinelCallback

    return SentinelCallback


def get_openai_wrapper():
    from .openai_wrapper import SentinelOpenAI

    return SentinelOpenAI


def get_fastapi_middleware():
    from .fastapi_middleware import SentinelMiddleware

    return SentinelMiddleware
