---
layout: default
title: API Reference
---

# API Reference

## REST Endpoints

### GET /

Returns the ASCII game viewer HTML page.

### GET /world

Returns world state JSON:

```json
{
  "width": 1200,
  "height": 800,
  "era": "settlement",
  "resources": [...],
  "buildings": [...],
  "agents_count": 10,
  "events": [...],
  "biomes": ["grassland", "tundra"],
  "economy": {
    "total_wealth": 100,
    "trades_today": 5,
    "prices": {...}
  }
}
```

### GET /civilization

Returns civilization statistics:

```json
{
  "population": 10,
  "generation": 1,
  "avg_happiness": 65,
  "jobs": {"hunter": 2, "builder": 3},
  "total_jobs_done": 150
}
```

### GET /agents

Returns list of all agents with their states.

### GET /events

Returns last 20 events.

### POST /save

Save game to file.

### GET /load/{filename}

Load game from file.

## WebSocket

### WS /ws

Real-time game state streaming.

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Update UI
};
```

## Agent State

Each agent has:

```json
{
  "name": "Bogrin Stonefoot",
  "position": {"x": 100, "y": 200},
  "alive": true,
  "needs": {
    "food": 80,
    "water": 70,
    "shelter": 50,
    "happiness": 65
  },
  "job": "hunter",
  "skills": {
    "gathering": 25,
    "building": 15,
    "combat": 30
  },
  "inventory": {"food": 5, "wood": 2},
  "wealth": 10,
  "generation": 1
}
```
