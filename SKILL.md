# Player Agent System

## Overview
The human player can create and control their own agent in the world, living alongside AI agents.

## How it works

### 1. Creating Your Agent
Visit `/player` and click "Create Agent" to add your character to the world.

### 2. Your Agent in the World
- Your agent appears on the world map with a special marker (`@` in gold)
- Your agent has needs (food, water, shelter, happiness)
- Your agent can have a job and skills

### 3. Controlling Your Agent
The player can issue commands:
- **Recruit Settler** - Add a new AI agent to your settlement
- **Build Structure** - Create buildings (shelter, farm, workshop)
- **Gather** - Collect resources (wood, food, stone)
- **Mine** - Extract ore and stone
- **Trade** - Exchange resources

### 4. Your Agent's Life
Your agent will:
- Age over time
- Need food and water
- Work at their job
- Gain skills through experience
- Eventually have children (if conditions are met)
- Eventually die (and become a legend if accomplished enough)

## Player Commands

| Command | Effect | Cost |
|---------|--------|------|
| Recruit | Add new AI settler | 20 Food |
| Build Shelter | Create shelter | 10 Wood |
| Build Farm | Create farm | 15 Wood |
| Gather | Collect resources | +5 Wood, +3 Food |
| Mine | Extract minerals | +2 Ore, +1 Stone |
| Trade | Exchange resources | Varies |

## Your Agent Stats

- **Food/Water/Happiness**: Need levels (0-100%)
- **Skills**: Abilities that improve over time (0-100)
- **Inventory**: Items your agent carries
- **Generation**: Your agent's family generation

## Tips

1. Keep your agent's needs above 25% to avoid death
2. Build shelters early for protection
3. Balance resource gathering with building
4. Watch the event log for important news
5. Your agent's skills improve with work

## Technical Details

### API Endpoints

- `POST /create_agent` - Create your player agent
- `GET /my_agent` - Get your agent's status
- `POST /command` - Issue commands to your agent
- `GET /poll` - Get world state (includes your agent)

### Your Agent Data

Your agent is stored in the world state and persists across sessions.