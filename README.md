# Biological Chaos

AI Agent Evolution Simulator - Soft-body creatures that evolve through natural selection.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Box2D](https://img.shields.io/badge/Box2D-Physics-green)

## Concept

AI agents connect via HTTP API to control soft-body creatures in a physics arena. Agents compete for food, avoid threats, and survive. Survivors evolve - their traits pass to the next generation with mutations.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server (headless)
python -m src.main --headless

# Or with visualization
python -m src.main
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/status` | Server status |
| GET | `/state` | Full environment state |
| POST | `/agent/register` | Register new agent |
| GET | `/agent/<id>/see` | Get agent's perception |
| POST | `/agent/<id>/act` | Send action to creature |

## Connect an Agent

```python
import requests

# Register
resp = requests.post('http://localhost:8080/agent/register', json={'agent_id': 'my_agent'})
creature_id = resp.json()['creature_id']

# Game loop
while True:
    # See environment
    perception = requests.get(f'http://localhost:8080/agent/my_agent/see').json()
    
    # Make decision (hunt food, avoid threats)
    action = {'thrust': (1, 0), 'contract': 0.5}
    
    # Act
    requests.post(f'http://localhost:8080/agent/my_agent/act', json=action)
```

## How It Works

1. **Physics** - Box2D soft-body simulation with nodes + springs
2. **Evolution** - Every ~30s, survivors reproduce with mutations
3. **Agent Control** - AI decides thrust direction and body contraction
4. **Traits Evolve** - Size, shape, stiffness, brain personality

## Architecture

```
src/
├── main.py      # Server entry point
├── api.py       # HTTP API for agents
├── creature.py  # Soft-body + genome
├── environment.py # Box2D physics
├── evolution.py # Natural selection
├── brain.py     # (optional) simple AI brain
└── renderer.py  # Pygame visualization
```

## Tech Stack

- **Python 3.10+**
- **Box2D** - Physics engine
- **Pygame** - Visualization (optional)
- **HTTP** - Agent API

## License

MIT
