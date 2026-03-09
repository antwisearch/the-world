# The World - Specification

## Concept

**The World** is a Dwarf Fortress-style colony simulation where AI agents live, work, build, trade, and create emergent stories. Players can watch as a civilization unfolds through agent decisions, random events, and complex systems.

## Current Implementation (Working)

### 1. World Environment ✅

- **Terrain:** Procedural generation with elevation, water sources, forests
- **Biomes:** 8 biome types (grassland, forest, desert, tundra, snow, jungle, swamp, savanna)
- **Resources:** Food, wood, stone, iron, gold, gems
- **Buildings:** Houses, farms, mines, workshops, shops, taverns
- **Weather:** Rain, snow, fog - affects agent happiness and farming
- **Seasons:** Spring, Summer, Fall, Winter - cycle affects food spawn rates

### 2. Agents ✅

**Needs System:**
- Food, water, shelter, happiness
- Sleep, comfort

**Jobs:**
- Farmer, gatherer, hunter, builder, miner, trader, guard, woodcutter, fisher

**Skills:**
- Agents gain XP in their job
- Skills affect productivity
- Can become legendary in their field

**Behavior:**
- Behavior Trees and Utility AI for decision making
- GOAP for multi-step planning
- Relationship system (family, friends, enemies)

**Biography:**
- Tracks life history
- Generates obituaries for dead agents
- Records kills, buildings, trades

### 3. Economy & Trading ✅

- Dynamic market pricing
- Gold-based economy
- Trade between agents
- Wandering traders with shops
- Player-run shops
- Trade history tracking

### 4. Events & Stories ✅

- Random world events
- Event chains (raiders → fortifications)
- Legends system (famous agents become legends)
- World history timeline
- Festivals, feuds, battles, romance

### 5. Technical Stack ✅

- **Python 3.12**
- **FastAPI** - Web server
- **WebSocket** - Real-time streaming
- **Thread-safe** simulation loop

## File Structure

```
biological-chaos/
├── SPEC.md                 # This file
├── README.md               # Overview
├── CHANGELOG.md            # Version history
├── DF_STYLE.md             # Design guidelines
├── requirements.txt        # Python dependencies
├── src/
│   ├── main.py            # Server entry
│   ├── api.py             # FastAPI server + WebSocket
│   ├── world.py           # World state + simulation
│   ├── agent.py           # Agent class + behavior
│   ├── civilization.py    # Population management
│   ├── biomes.py          # Biome resources
│   ├── terrain.py         # Terrain generation
│   ├── buildings.py       # Building types
│   ├── jobs.py            # Job behaviors
│   ├── economy.py         # Economic system
│   ├── trading.py         # Trade system
│   ├── events.py          # Random events
│   ├── event_chains.py    # Linked events
│   ├── more_events.py     # Additional events
│   ├── seasonal_events.py # Season-specific events
│   ├── seasons.py         # Season cycling
│   ├── weather.py         # Weather system
│   ├── relationships.py   # Family & friends
│   ├── biography.py       # Agent life stories
│   ├── legends.py         # Legendary agents
│   ├── history.py         # World timeline
│   ├── goap.py           # Goal-oriented action planning
│   ├── utility_ai.py     # Behavior Trees
│   ├── pathfinding.py    # A* pathfinding
│   ├── names.py          # Name generation
│   ├── resources.py      # Resource types
│   ├── artifacts.py      # Artifact generation
│   ├── save_manager.py   # Save/Load JSON
│   ├── config.py         # Settings
│   ├── websocket.py      # WS utilities
│   └── static/          # HTML/JS UI
└── saves/               # Saved games
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | ASCII game viewer |
| `/world` | GET | World state |
| `/civilization` | GET | Population stats |
| `/agents` | GET | Agent list |
| `/agent/{id}` | GET | Single agent |
| `/agent/register` | POST | Register new agent |
| `/agent/{id}/act` | POST | Agent action |
| `/events` | GET | Event log |
| `/trading/offers` | GET | Trade offers |
| `/trading/market` | GET | Market prices |
| `/trading/history` | GET | Trade history |
| `/trading/items` | GET | Tradable items |
| `/trading/traders` | GET | Active traders |
| `/trading/shops` | GET | All shops |
| `/save` | POST | Save game |
| `/load/{filename}` | GET | Load game |
| `/saves` | GET | List saves |
| `/ws` | WS | Real-time updates |

## Quick Start

```bash
cd biological-chaos
source venv/bin/activate
python -m src.api
```

Open http://localhost:8080 in your browser.

---

## Planned Improvements

### Phase 1: Quick Wins

1. **More Job Types**
   - Teacher (increases learning rate)
   - Healer (restores agent health)
   - Researcher (generates inventions)
   - Diplomat (improves relations with other groups)

2. **Enhanced UI**
   - Improve ASCII view with better symbols
   - Add mini-map
   - Show agent needs as colored bars

3. **Unit Tests**
   - Test agent behavior
   - Test economy calculations
   - Test trading system

### Phase 2: Expanded Systems

4. **Combat System**
   - Weapons and armor crafting
   - Siege warfare
   - Agent vs agent combat AI

5. **Disease System**
   - Sickness spreading
   - Doctors treating patients
   - Quarantine mechanics

6. **More Event Types**
   - Plagues
   - Migrations
   - Discovery of ruins
   - Trade caravans

### Phase 3: Advanced Features

7. **Multi-world Support**
   - Connect multiple servers
   - Trade between worlds

8. **Advanced AI**
   - Better GOAP planning
   - Learning from past decisions
   - Agent memory improvements

9. **Modding Support**
   - JSON-based config for new biomes/items
   - Scriptable events

---

## Future Vision (Optional Expansion)

The original SPEC.md described a *co-evolution simulation* with soft-body creatures and world-guided evolution. This could be added as a separate "Evolution Mode" in the future, but the current colony sim is the working foundation.

---

## Contributing

1. Fork the repo
2. Create a branch
3. Make changes
4. Submit PR

## License

MIT
