"""
Persistence — save and restore organism state.
"""

import json
import os
import time
from typing import Any, Dict, Optional
from pathlib import Path


class PersistenceLayer:
    """Save and load organism state."""

    def __init__(self, path: str = None, auto_save_interval: int = 50):
        self.path = path or "./sentinel_state"
        self.auto_save_interval = auto_save_interval
        self._observation_count = 0
        self._last_save = 0
        Path(self.path).mkdir(parents=True, exist_ok=True)

    def save(self, state: Dict[str, Any]) -> bool:
        try:
            state_file = os.path.join(self.path, "organism_state.json")
            temp_file = state_file + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump({"version": 2, "saved_at": time.time(), "state": state}, f, indent=2, default=str)
            os.replace(temp_file, state_file)
            self._last_save = time.time()
            return True
        except Exception:
            return False

    def load(self) -> Optional[Dict[str, Any]]:
        state_file = os.path.join(self.path, "organism_state.json")
        if not os.path.exists(state_file):
            return None
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("version") != 2:
                return None
            return data.get("state")
        except Exception:
            return None

    def save_baselines(self, baselines: Dict) -> bool:
        try:
            bl_file = os.path.join(self.path, "baselines.json")
            serialized = {}
            for metric, bl in baselines.items():
                serialized[metric] = {
                    "mean": bl.mean,
                    "variance": bl.variance,
                    "count": bl.count,
                    "lambda": bl.lambda_,
                    "history_length": len(bl.history),
                    "recent_values": [
                        {
                            "value": h.value,
                            "z_score": h.z_score,
                            "baseline": h.baseline,
                            "timestamp": h.timestamp,
                        }
                        for h in bl.history[-100:]
                    ],
                }
            with open(bl_file, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2)
            return True
        except Exception:
            return False

    def load_baselines(self) -> Optional[Dict]:
        bl_file = os.path.join(self.path, "baselines.json")
        if not os.path.exists(bl_file):
            return None
        try:
            with open(bl_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save_memories(self, memories: list) -> bool:
        try:
            mem_file = os.path.join(self.path, "memories.json")
            serialized = [
                {
                    "event": m.event,
                    "context": m.context,
                    "outcome": m.outcome,
                    "fix": m.fix,
                    "timestamp": m.timestamp,
                    "tags": m.tags,
                }
                for m in memories
            ]
            with open(mem_file, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2, default=str)
            return True
        except Exception:
            return False

    def load_memories(self) -> Optional[list]:
        mem_file = os.path.join(self.path, "memories.json")
        if not os.path.exists(mem_file):
            return None
        try:
            with open(mem_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def tick(self):
        self._observation_count += 1
        return self._observation_count % self.auto_save_interval == 0

    def exists(self) -> bool:
        return os.path.exists(os.path.join(self.path, "organism_state.json"))

    def age(self) -> Optional[float]:
        state_file = os.path.join(self.path, "organism_state.json")
        if not os.path.exists(state_file):
            return None
        return time.time() - os.path.getmtime(state_file)

    def clear(self):
        import shutil

        if os.path.exists(self.path):
            shutil.rmtree(self.path)
            Path(self.path).mkdir(parents=True, exist_ok=True)
