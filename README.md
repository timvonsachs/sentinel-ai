# 🛡️ Sentinel AI

### Your AI has a brain. We give it a body.

Every AI system deployed today is a brain in a jar. It can think, but it can't feel. It doesn't know when it's getting worse. It can't heal itself. It has no immune system.

**Sentinel changes that.**

## Quick Start

```bash
pip install sentinel-ai
```

```python
from sentinel import Organism

# Your AI is now alive
body = Organism("my-agent", autonomous=True)

# Observe any metric
body.observe("conversion_rate", 0.34)
body.observe("satisfaction", 4.2)
body.observe("hallucination_rate", 0.03)

# Check health
print(body.status)   # "healthy"
print(body.pain)     # 0.12
print(body.feeling)  # "Healthy. Minor fluctuations."

# The AI knows when it's sick
health = body.immune.health("conversion_rate")
if health.status == "warning":
    # Self-healing: the AI fixes itself
    body.memory.recall("drift")  # What worked last time?
```

## The Biology of AI

| System | Human | AI Equivalent | Status |
|--------|-------|---------------|--------|
| 🛡️ Immune | Fights infection | Drift detection + self-healing | ✅ Active |
| ⚡ Nervous | Reflexes | Real-time safety triggers | ✅ Active |
| 🧬 Endocrine | Hormonal regulation | Long-term parameter adaptation | ✅ Active |
| 🧠 Memory | Experiential learning | Historical pattern recognition | ✅ Active |
| ⚠️ Pain | "Something's wrong" | Composite health intuition | ✅ Active |
| 💧 Lymphatic | Detox & cleanup | Bias & hallucination removal | 🔜 Coming |
| 🔒 Skin | Barrier & defense | Prompt injection protection | 🔜 Coming |
| 💨 Respiratory | Energy regulation | Compute self-optimization | 🔜 Coming |
| ❤️ Circulatory | Nutrient transport | Cross-component state flow | 🔜 Coming |
| 🌱 Reproductive | Evolution | Autonomous self-improvement | 🔜 Coming |
| 🐙 Octopus | Distributed intelligence | Per-component awareness | 🔜 Coming |

## Origin Story

I'm bipolar. My brain lies to me. During mania, I feel invincible while my life falls apart. During depression, I feel hopeless while reality is fine.

So I built NOVA — an early warning system that monitors my voice daily and tells me when I'm drifting from my own baseline. It detected my last episode 11 days before I noticed it myself.

Then I realized: **every AI system has the same problem.** Billions of AI systems deployed worldwide. All without self-awareness. All blind to their own drift.

I'm taking what I built for my own mind and giving it to every AI on the planet.

## License

MIT — Free forever. Because every AI deserves a body.
