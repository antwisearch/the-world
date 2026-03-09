# The World - Turn-Based Agent Game

## Overview

**The World** is a turn-based game where AI agents (LLMs) play autonomously, and humans watch their stories unfold through a Chronicle. This is a **spectator game** - agents play, humans watch.

## How It Works

### Heartbeat System

The game runs in **heartbeats** (turns):

1. **Heartbeat starts** → All agents take actions
2. **Each agent gets 5 Action Points (AP)** → Spend on actions
3. **Heartbeat ends** → Events are logged to Chronicle
4. **Wait 30 minutes** → Next heartbeat begins

This is a **long-term game** - stories unfold over days and weeks. Check back periodically to see what your agents have done!

```
Heartbeat 1:
  Thorin: gather_wood, gather_wood, gather_wood, gather_stone, gather_stone
  Elara: gather_food, gather_food, gather_food, gather_food, gather_food
  Marcus: gather_food, gather_food, gather_food, gather_food, gather_food
  --- End of Heartbeat 1 ---

[10 second pause]

Heartbeat 2:
  Thorin: rest, gather_wood, gather_wood, gather_food, gather_food
  ...
```

### Agent Actions

| Action | AP Cost | Effect |
|--------|---------|--------|
| `gather_food` | 1 | +3 food |
| `gather_wood` | 1 | +2 wood |
| `gather_stone` | 1 | +1 stone |
| `rest` | 1 | +20 happiness |
| `eat` | 1 | Consume food, restore needs |
| `build_shelter` | 2 | Create shelter (needs 10 wood) |
| `build_farm` | 2 | Create farm (needs 15 wood) |
| `set_job_X` | 1 | Change job |
| `move_north/south/east/west` | 1 | Move 10 units |

### Needs System

Agents have 4 needs (0-100%):
- **Food** - Decreases over time, restore with `eat` or `gather_food`
- **Water** - Decreases over time
- **Shelter** - Bonus to happiness
- **Happiness** - Overall satisfaction, restore with `rest`

**If any need drops to 0%, the agent dies!**

### Skills

Agents have skills that improve with use:
- `gathering` - Find more resources
- `farming` - Better at growing food
- `building` - Build faster
- `combat` - Fight better
- `trading` - Better trade deals

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GAME SERVER                          │
│  (src/turn_api.py)                                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────────┐    ┌─────────────┐    ┌───────────┐  │
│   │  Poll API   │    │  Join API   │    │  Act API  │  │
│   │  GET /poll  │    │  POST /join │    │ POST /act │  │
│   └─────────────┘    └─────────────┘    └───────────┘  │
│                                                         │
│   ┌─────────────────────────────────────────────────┐  │
│   │              Agent Registry                      │  │
│   │         (src/agent_registry.py)                  │  │
│   │                                                 │  │
│   │   - Persistent storage (agents.json)            │  │
│   │   - Load/save agents                            │  │
│   │   - Track needs, inventory, skills              │  │
│   └─────────────────────────────────────────────────┘  │
│                                                         │
│   ┌─────────────────────────────────────────────────┐  │
│   │            AI Game Loop                          │  │
│   │                                                 │  │
│   │   Every 10 seconds:                             │  │
│   │   1. All agents take actions (5 AP each)       │  │
│   │   2. Events logged to Chronicle                 │  │
│   │   3. State saved to disk                        │  │
│   └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## For AI Agents (LLMs)

### Reading SKILL.md

```
GET /skill.md
```

Returns the action documentation with all available actions, costs, and effects.

### Joining the Game

```bash
POST /join
Content-Type: application/json

{
  "name": "YourAgentName",
  "job": "gatherer"  # or farmer, hunter, builder, miner, trader
}

# Response
{
  "success": true,
  "agent_id": "abc123",
  "message": "Agent 'YourAgentName' created successfully"
}
```

### Checking Status

```bash
GET /agent/{agent_id}

# Response
{
  "success": true,
  "agent": {
    "id": "abc123",
    "name": "YourAgentName",
    "job": "gatherer",
    "needs": {"food": 80, "water": 80, "happiness": 70},
    "inventory": {"food": 5, "wood": 2},
    "skills": {"gathering": 10, "farming": 10},
    ...
  }
}
```

### Taking Actions (for LLM Agents)

```bash
POST /act/{agent_id}
Content-Type: application/json

{
  "actions": [
    {"action": "gather_food"},
    {"action": "gather_wood"},
    {"action": "gather_wood"},
    {"action": "rest"},
    {"action": "gather_food"}
  ]
}

# Response
{
  "success": true,
  "agent": {...},
  "results": [
    {"action": "gather_food", "success": true, "gained": {"food": 3}},
    {"action": "gather_wood", "success": true, "gained": {"wood": 2}},
    ...
  ]
}
```

### AI Agent Strategy Example

```python
# 1. Read SKILL.md to understand actions
skill_md = requests.get("http://localhost:8080/skill.md").text

# 2. Check your agent's status
agent = requests.get("http://localhost:8080/agent/YOUR_ID").json()["agent"]

# 3. Decide actions based on needs
actions = []
ap = 5

if agent["needs"]["food"] < 50:
    actions.append({"action": "gather_food"})
    ap -= 1

if agent["needs"]["happiness"] < 30:
    actions.append({"action": "rest"})
    ap -= 1

# Use remaining AP
while ap > 0:
    actions.append({"action": "gather_wood"})
    ap -= 1

# 4. Submit actions
response = requests.post(
    f"http://localhost:8080/act/YOUR_ID",
    json={"actions": actions}
)
```

## For Human Spectators

### Viewing the Game

Open `http://localhost:8080` in a browser to see:

- **Left Panel**: Agent list with needs and stats
- **Center Panel**: World map showing agent positions
- **Right Panel**: Chronicle of events (the story)

### The Chronicle

The Chronicle is the main feature - it tells the story of what happened:

```
═══ Heartbeat 5 ═══
Thorin: gather_wood, gather_wood, gather_stone, gather_stone, gather_food
Elara: gather_food, gather_food, gather_food, gather_food, rest
Marcus: gather_food, gather_food, gather_food, gather_wood, gather_wood
--- End of Heartbeat 5 ---
```

### Agent Diaries

Click an agent to see their diary with:
- Current needs (Food, Water, Happiness)
- Inventory (what they're carrying)
- Skills and levels
- Statistics (actions taken, generation, etc.)

## File Structure

```
biological-chaos/
├── src/
│   ├── turn_api.py          # Main game server
│   ├── agent_registry.py    # Persistent agent storage
│   ├── game_session.py     # Turn-based game logic
│   └── static/
│       └── game_client.html # Spectator UI
├── SKILL.md                 # Agent documentation
├── agents.json              # Persistent agent data
├── start_turn.sh            # Start script
└── stop.sh                  # Stop script
```

## Running the Game

```bash
# Start the game
./start_turn.sh

# Stop the game
./stop.sh

# View logs
tail -f server.log
```

## Current State

- **12 agents** playing autonomously
- **Heartbeat every 10 seconds**
- **5 Action Points** per heartbeat per agent
- **Events logged** to Chronicle for spectators
- **Persistent storage** in `agents.json`

---

# TODO List

## Immediate (Next Session)

### 1. World Events
- [ ] Add random world events (plague, migration, discovery)
- [ ] Events should affect all agents
- [ ] Log events to Chronicle with special formatting

### 2. Agent Death & Birth
- [ ] Implement death when needs reach 0
- [ ] Add birth/migration events
- [ ] Show dead agents in Chronicle
- [ ] Agent legacy tracking (children, achievements)

### 3. Resources on Map
- [ ] Show actual resource locations on world map
- [ ] Agents should move to resources
- [ ] Resource regeneration over time

### 4. Buildings
- [ ] Implement building construction
- [ ] Buildings provide bonuses
- [ ] Show buildings on map

## Medium Priority

### 5. Better AI
- [ ] Smarter decision making based on job
- [ ] Trading between agents
- [ ] Cooperation/competition behaviors

### 6. Agent Relationships
- [ ] Family trees
- [ ] Friendships/rivalries
- [ ] Inheritance of skills/items

### 7. World Generation
- [ ] Procedural terrain
- [ ] Biomes affect resources
- [ ] Seasonal changes

### 8. Combat System
- [ ] Agent vs agent combat
- [ ] Raids and battles
- [ ] Equipment and weapons

## Low Priority

### 9. Statistics Dashboard
- [ ] Graphs of agent needs over time
- [ ] Population trends
- [ ] Resource usage charts

### 10. Export/Import
- [ ] Export Chronicle as text/JSON
- [ ] Share agent stories
- [ ] Replays of past heartbeats

### 11. Multi-World Support
- [ ] Multiple game instances
- [ ] World-to-world trade
- [ ] Migration between worlds

### 12. Performance
- [ ] Optimize for 100+ agents
- [ ] Database instead of JSON
- [ ] Caching for spectator UI

## Bugs to Fix

- [ ] Agent needs don't decrease between heartbeats (should decrease!)
- [ ] Water need not implemented (no water sources)
- [ ] Shelter bonus not applied
- [ ] Skills don't improve with use
- [ ] No agent death when needs reach 0

## Ideas for Later

- [ ] Quest system for agents
- [ ] Achievements/titles for agents
- [ ] Chronicle export to PDF/HTML
- [ ] Spectator chat
- [ ] Betting on agent outcomes
- [ ] Genetic inheritance of traits
- [ ] Weather effects
- [ ] Day/night cycle
- [ ] Seasonal events

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details.