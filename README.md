# The World - Dwarf Fortress Style Colony Simulation

A procedural colony simulation where AI agents live, work, and create emergent stories.

## Quick Start

```bash
cd biological-chaos
source venv/bin/activate
python -m src.api
```

Then open http://localhost:8080 in your browser.

## Architecture

### Core Modules

| File | Purpose |
|------|---------|
| `world.py` | Main simulation loop, manages agents/resources/buildings |
| `agent.py` | Individual agents with needs, jobs, skills |
| `civilization.py` | Population management, births, immigration |
| `api.py` | FastAPI server with WebSocket streaming |

### AI & Behavior

| File | Purpose |
|------|---------|
| `utility_ai.py` | Behavior Trees, Utility AI for decisions |
| `pathfinding.py` | A* pathfinding |
| `behaviors.py` | Legacy AI behaviors |

### Generation

| File | Purpose |
|------|---------|
| `terrain.py` | Perlin noise, biome generation |
| `biomes.py` | Biome-specific resources, quest system |
| `names.py` | Dwarf Fortress-style name generation |

### Systems

| File | Purpose |
|------|---------|
| `biography.py` | Agent life stories, achievements |
| `history.py` | World timeline, historical events |
| `legends.py` | Legendary figures |
| `relationships.py` | Family, friends, enemies |
| `artifacts.py` | Items dropped by dead agents |
| `events.py` | Random events (raiders, discoveries, etc.) |
| `event_chains.py` | Events that trigger follow-up events |
| `more_events.py` | Romance, feuds, festivals |

### Data

| File | Purpose |
|------|---------|
| `resources.py` | Resource types and spawning |
| `buildings.py` | Building types (shelter, farm, workshop) |
| `jobs.py` | Job behaviors (gatherer, builder, hunter, etc.) |

### Infrastructure

| File | Purpose |
|------|---------|
| `save_manager.py` | Save/load game state |
| `websocket.py` | WebSocket handling |

## API Endpoints

- `GET /` - ASCII viewer
- `GET /world` - World state
- `GET /civilization` - Civ stats
- `GET /agents` - Agent list
- `GET /events` - Event log
- `POST /save` - Save game
- `GET /ws` - WebSocket stream

## Game Concepts

### Agents
- Have needs: food, water, shelter, happiness
- Have jobs: gatherer, builder, hunter, farmer, trader, guard
- Gain skills through work
- Can become legends

### World
- Procedural biomes (grassland, forest, desert, tundra, etc.)
- Resources spawn based on biome
- Random events create stories
- History recorded over time

### Emergent Stories
- Named agents with biographies
- Causes of death tracked
- Legends remembered
- Events chain into storylines

## Tech Stack

- Python 3.12
- FastAPI (web server)
- WebSocket (real-time streaming)
- No external game engine - pure Python

## Legacy Files

The following files are from older versions and not currently used:
- `creature.py` - Old creature system
- `evolution.py` - Old evolution system
- `brain.py` - Legacy AI
- `renderer.py` - Old renderer
- `environment.py` - Old environment
- `save.py` - Old save system

## Contributing

1. Check GitHub issues
2. Make changes in a branch
3. Submit PR
4. Test locally first
