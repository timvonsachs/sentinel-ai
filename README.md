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

## The Complete Organism

Sentinel `v0.2.0` includes **20 integrated modules**:
**11 biological systems + 5 animal capabilities + 4 transcendent abilities**.

### 11 Biological Systems

| System | Human | AI Equivalent | Status |
|--------|-------|---------------|--------|
| 🛡️ Immune | Fights infection | Drift detection + self-healing | ✅ Active |
| ⚡ Nervous | Reflexes | Real-time safety triggers | ✅ Active |
| 🧬 Endocrine | Hormonal regulation | Long-term parameter adaptation | ✅ Active |
| 🧠 Memory | Experiential learning | Historical pattern recognition | ✅ Active |
| ⚠️ Pain | "Something's wrong" | Composite health intuition | ✅ Active |
| 🔒 Skin | Barrier & defense | Prompt injection and threat filtering | ✅ Active |
| 💧 Lymphatic | Detox & cleanup | Bias/convergence contamination scanning | ✅ Active |
| ❤️ Circulatory | State flow | Cross-component packet bus | ✅ Active |
| 🔄 Digestive | Nutrient extraction | Input quality filtering + enrichment | ✅ Active |
| 💨 Respiratory | Breathing | Dynamic compute budget regulation | ✅ Active |
| 🌱 Reproductive | Evolution | Autonomous variant generation and selection | ✅ Active |

### 5 Animal Capabilities

| Capability | Inspiration | AI Power | Status |
|------------|-------------|----------|--------|
| 🐙 Octopus | 9 distributed brains | Per-component autonomous awareness | ✅ Active |
| 🦎 Chameleon | Instant context adaptation | Real-time parameter adaptation by signals | ✅ Active |
| 🐻 Tardigrade | Cryptobiosis survival | Controlled hibernation / safe mode | ✅ Active |
| 🦎 Salamander | Limb regeneration | Component rebuild and recovery | ✅ Active |
| 🍄 Swarm | Mycelium intelligence | Shared immunity + collective learning | ✅ Active |

### 4 Transcendent Abilities

| Ability | Beyond Biology | AI Power | Status |
|---------|----------------|----------|--------|
| 🔮 Oracle | Future simulation | Multi-scenario shadow outcomes | ✅ Active |
| 🧿 Telepathy | Direct memory transfer | Experience packets across organisms | ✅ Active |
| 🔥 Phoenix | Metamorphosis | Form switching and architecture adaptation | ✅ Active |
| ♾️ Immortal | Evolving without dying | Champion/challenger continuous evolution | ✅ Active |

## Demos

- `python3 examples/quickstart.py`
- `python3 examples/full_organism.py`
- `python3 examples/swarm_demo.py`
- `python3 examples/evolution_demo.py`

## Origin Story

I'm bipolar. My brain lies to me. During mania, I feel invincible while my life falls apart. During depression, I feel hopeless while reality is fine.

So I built NOVA — an early warning system that monitors my voice daily and tells me when I'm drifting from my own baseline. It detected my last episode 11 days before I noticed it myself.

Then I realized: **every AI system has the same problem.** Billions of AI systems deployed worldwide. All without self-awareness. All blind to their own drift.

I'm taking what I built for my own mind and giving it to every AI on the planet.

## License

MIT — Free forever. Because every AI deserves a body.
