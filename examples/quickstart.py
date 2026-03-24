"""
Quickstart: Give your AI an immune system in 3 lines.
"""

import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sentinel import Organism

random.seed(42)

# Create a living AI system
body = Organism("my-sales-agent", autonomous=True)

runtime = {"day": 0, "healed": False, "heal_day": None}


def switch_to_safe_prompt(alert):
    """Example healer: switch runtime to safe prompt profile."""
    if not runtime["healed"]:
        runtime["healed"] = True
        runtime["heal_day"] = runtime["day"]


# Register self-healing hook
body.immune.on_warning("conversion", switch_to_safe_prompt)
body.immune.on_critical("conversion", switch_to_safe_prompt)

print("Day | Conversion | Z-Score | Status     | Pain  | Feeling")
print("-" * 75)

for day in range(1, 31):
    runtime["day"] = day

    # Normal days 1-10
    if day <= 10:
        conversion = 0.37 + random.gauss(0, 0.006)
    # Controlled drift until healer kicks in
    elif not runtime["healed"]:
        drift = (day - 10) * 0.0045
        conversion = 0.37 - drift + random.gauss(0, 0.006)
    # Recovery after self-healing
    else:
        conversion = 0.362 + random.gauss(0, 0.005)

    obs = body.observe("conversion", conversion)
    health = body.immune.health("conversion")

    status_emoji = {
        "learning": "📚",
        "healthy": "💚",
        "thriving": "🌟",
        "watch": "👀",
        "warning": "⚠️",
        "critical": "🚨",
    }

    emoji = status_emoji.get(health.status.value, "❓")
    heal_marker = " ✅ heal" if runtime["healed"] and day >= runtime["heal_day"] else ""
    print(
        f" {day:2d}  | {conversion:.3f}    | {obs.z_score:+.2f}   "
        f"| {emoji} {health.status.value:10s} | {body.pain:.2f}  | {body.feeling}{heal_marker}"
    )
