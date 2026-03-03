# The World

A co-evolution simulation where AI agents shape their environment, and the environment shapes what creatures evolve.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Box2D](https://img.shields.io/badge/Box2D-Physics-green)

## Concept

**The World** is not just an arena - it's a living, changing ecosystem. AI agents control soft-body creatures that:

1. **Shape the world** - Build structures, start fires, modify terrain
2. **Adapt to the world** - Evolution selects for traits matching current world state
3. **Go through eras** - Primordial → Age of Fire → Ice Age → Urban → Collapse

The world responds to collective agent behavior. Enough fires? The world enters the **Age of Fire**. Build 100 structures? Enter the **Urban** era.

## Quick Start

```bash
pip install -r requirements.txt
python -m src.main
```

## How It Works

### The World State
- Climate zones (hot, temperate, cold)
- Weather events (rain, drought, fire, flood)
- Era that shifts based on agent collective action
- Terrain with elevation and structures

### Evolution
Creatures evolve traits based on world conditions:
- Fire world → fire-resistant creatures
- Cold world → cold-hardy creatures  
- Urban world → spatial intelligence
- Scarcity → efficient metabolisms

### Eras
| Era | Trigger | World |
|-----|---------|-------|
| Primordial | Start | Warm, abundant |
| Age of Fire | 50 fires | Hot, dangerous |
| Ice Age | Temp < 0 | Frozen |
| Urban | 100 structures | Built environment |
| Collapse | 200+ fires | Harsh, scarce |

## API

```python
import requests

# Register
resp = requests.post('http://localhost:8080/agent/register', json={'agent_id': 'my_agent'})

# See what your creature perceives (world state + local environment)
perception = requests.get('http://localhost:8080/agent/my_agent/perceive').json()

# Act
requests.post('http://localhost:8080/agent/my_agent/act', json={
    'move': (1, 0.5),
    'contract': 0.3,
    'build': 'wall'  # Optional world modification
})
```

## Architecture

```
src/
├── main.py      # Server entry
├── world.py     # World state + climate
├── creature.py  # Soft body + genome
├── physics.py   # Box2D wrapper
├── climate.py   # Weather system
├── terrain.py   # Elevation + structures
├── evolution.py # World-guided evolution
├── api.py       # FastAPI server
└── agent.py     # Agent connection
```

## The Vision

Watch as:
- Different climates produce different creature species
- Creatures evolve to exploit new niches
- Agent societies build and destroy
- The world goes through epochs
- Intelligence emerges from chaos

This is not a game you play - it's a world you observe and influence.

## Tech Stack

- Python 3.10+
- Box2D (physics)
- FastAPI (agent API)
- Pygame (optional visualization)

## License

MIT
