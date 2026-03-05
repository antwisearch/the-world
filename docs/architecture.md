---
layout: default
title: Architecture
---

# Architecture

## Overview

The World uses a modular architecture with separate systems for AI, generation, and simulation.

## Core Modules

### world.py

Main simulation loop. Manages:
- Agents list
- Resources
- Buildings
- Events
- Updates every tick

```python
world = World()
world.update(dt)  # Called 60 times per second
```

### agent.py

Individual agents with:
- Needs (food, water, shelter, happiness)
- Job assignment
- Skills
- Inventory
- Biography

```python
agent = Agent(x, y)
agent.do_job(world)
agent.update_needs(dt)
```

### api.py

FastAPI server providing:
- REST endpoints
- WebSocket streaming
- Static file serving

## AI Systems

### utility_ai.py

Behavior Trees + Utility AI for agent decision making.

```python
action, priority = BehaviorTree.evaluate(agent, world)
scores = UtilityScore.score_needs(agent)
```

### goap.py

GOAP (Goal-Oriented Action Planning) for complex tasks.

```python
plan = plan_for_goal(agent, world, {'food': 20})
```

## Generation

### terrain.py

Perlin noise for terrain generation:
- Temperature
- Rainfall  
- Elevation
- Biomes

### biomes.py

Biome-specific resource spawning:
- Each biome has unique resources
- Quest generation

## Systems

### economy.py

Market and trade:
- Dynamic pricing
- Agent-to-agent trading
- Wealth tracking

### history.py

World timeline:
- Births, deaths
- Battles, disasters
- Legendary events

### legends.py

Famous figures:
- Track achievements
- Generate titles
- Record famous deaths
