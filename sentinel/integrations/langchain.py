"""
LangChain Integration — Automatic organism instrumentation.
"""

from typing import Dict, List
import time

from ..core.event_bus import Event


class SentinelCallback:
    """LangChain callback handler that feeds the organism."""

    def __init__(self, organism):
        self.organism = organism
        self._call_start_times: Dict[str, float] = {}

    def on_llm_start(self, serialized: Dict, prompts: List[str], run_id: str = None, **kwargs):
        _ = serialized, kwargs
        rid = str(run_id) if run_id else str(time.time())
        self._call_start_times[rid] = time.time()
        for prompt in prompts:
            result = self.organism.process_input(prompt)
            if not result.get("safe"):
                self.organism.bus.emit(
                    Event(
                        type="langchain.unsafe_prompt",
                        source="langchain",
                        data={"threats": result.get("threats", [])},
                        severity=3,
                    )
                )

    def on_llm_end(self, response, run_id: str = None, **kwargs):
        _ = kwargs
        rid = str(run_id) if run_id else ""
        start = self._call_start_times.pop(rid, time.time())
        latency = (time.time() - start) * 1000
        self.organism.observe("latency", latency)

        if hasattr(response, "generations") and response.generations:
            for gen in response.generations:
                for g in gen:
                    if hasattr(g, "text"):
                        self.organism.observe("response_length", len(g.text))
                        self.organism.process_output(g.text)

        self.organism.signal({"latency": latency})

    def on_llm_error(self, error: Exception, **kwargs):
        _ = kwargs
        self.organism.observe("error_rate", 1.0)
        self.organism.bus.emit(
            Event(
                type="langchain.error",
                source="langchain",
                data={"error": str(error)},
                severity=3,
            )
        )

    def on_chain_start(self, serialized: Dict, inputs: Dict, **kwargs):
        _ = serialized, inputs, kwargs

    def on_chain_end(self, outputs: Dict, **kwargs):
        _ = outputs, kwargs

    def on_tool_start(self, serialized: Dict, input_str: str, **kwargs):
        _ = serialized, input_str, kwargs

    def on_tool_end(self, output: str, **kwargs):
        _ = kwargs
        self.organism.process_output(output)
