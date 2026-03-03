# The World - Dwarf Fortress Style

## Concept
A colony simulation where AI agents build, gather, trade, and survive. Emergent storytelling through agent interactions.

## Core Systems

### Agents
- **Needs**: food, water, shelter, happiness
- **Jobs**: gatherer, builder, trader, hunter, farmer
- **Skills**: combat, building, gathering, trading
- **Inventory**: resources and items

### World
- **Resources**: food, wood, stone, ore (spawn naturally)
- **Structures**: shelters, farms, workshops, stockpiles
- **Zones**: gathering areas, building areas

### Economy
- Trading between agents
- Resource exchange

## Changes from Original

### creature.py → agent.py
- Needs system (food, water, shelter, happiness)
- Job assignment
- Skill progression
- Inventory

### world.py
- Resource spawning (more dynamic)
- Building system
- Zone management

### evolution.py → civilization.py
- Population management (births, deaths)
- Trade system
- Event logging
