# The World

A Dwarf Fortress-style colony simulation where AI agents live, work, and create emergent stories.

![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Quick Start

```bash
# Clone and run
git clone https://github.com/antwisearch/the-world.git
cd the-world
source venv/bin/activate
python -m src.api
```

Open http://localhost:8080 in your browser.

## What is The World?

The World is a procedural colony simulation where:
- AI agents have needs (food, water, shelter, happiness)
- Agents have jobs (gatherer, builder, hunter, farmer, trader, guard)
- Agents gain skills and can become legendary
- The world generates biomes, resources, and events
- Stories emerge from the simulation

## Features

### 🤖 AI Agents
- Named agents with Dwarf Fortress-style names
- Biographies tracking life history
- Relationship system (family, friends, enemies)
- Behavior Trees and Utility AI for decision making
- GOAP for multi-step planning

### 🌍 Procedural World
- Perlin noise terrain generation
- 8 biome types (grassland, forest, desert, tundra, snow, jungle, swamp, savanna)
- Biome-specific resources
- A* pathfinding

### 📜 Emergent Storytelling
- Death records with causes
- Legends system
- World history timeline
- Event chains (raiders → fortifications)
- Romance, feuds, festivals, battles

### 💰 Economy
- Market with dynamic pricing
- Trade between agents
- Wealth accumulation

### 💾 Save/Load
- Save game state to JSON
- Load saved games

## Architecture

```
src/
├── agent.py          # Agent class
├── api.py            # FastAPI server
├── biomes.py         # Biome resources
├── buildings.py      # Building types
├── civilization.py   # Population management
├── config.py        # Game settings
├── economy.py       # Trade & wealth
├── events.py        # Random events
├── goap.py         # Goal-oriented action planning
├── history.py       # World timeline
├── legends.py       # Legendary figures
├── names.py        # Name generation
├── relationships.py # Family & friends
├── terrain.py      # Perlin noise terrain
└── utility_ai.py  # Behavior Trees
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | ASCII game viewer |
| `/world` | GET | World state |
| `/agents` | GET | Agent list |
| `/events` | GET | Event log |
| `/save` | POST | Save game |
| `/ws` | WS | Real-time updates |

## Tech Stack

- **Python 3.12**
- **FastAPI** - Web server
- **WebSocket** - Real-time streaming
- **No external game engine** - Pure Python

## Contributing

1. Fork the repo
2. Create a branch
3. Make changes
4. Submit PR

## License

MIT

## Links

- [GitHub](https://github.com/antwisearch/the-world)
- [Issues](https://github.com/antwisearch/the-world/issues)
