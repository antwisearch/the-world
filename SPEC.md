# Biological Chaos - Specification

## Concept
Soft-body creatures that evolve through natural selection based on survival. Agents compete in a physics-based arena where traits like speed, size, shape, and elasticity determine survival.

## Core Mechanics

### Creatures (Soft Bodies)
- Made of connected nodes with spring joints
- Each node has: position, velocity, mass, color
- Nodes connected by springs (distance joints)
- Properties: flexibility, friction, restitution (bounciness)

### Evolution System
- **Survival of the fittest**: Creatures that survive longest reproduce
- **Mutation**: Offspring inherit traits with random variations
- **Traits that evolve**:
  - Body size (larger = more momentum, harder to push)
  - Number of nodes (more nodes = more complex shapes)
  - Spring stiffness (stiffer = rigid, looser = squishy)
  - Node mass distribution
  - Color (aesthetic, maybe affects heat absorption)

### Environment
- Physics world with gravity
- Food sources that spawn randomly
- Hazards (spikes, pits, other creatures)
- Boundaries that keep creatures in arena

### Simulation Loop
1. Spawn initial population (random creatures)
2. Run physics simulation
3. Creatures compete for food, avoid hazards
4. Survivors reproduce (clone + mutate)
5. Weakest die off
6. Repeat generations

## Tech Stack
- **Language**: Python
- **Physics**: Box2D (via pygame-box2d or similar)
- **Rendering**: Pygame for visualization
- **AI**: Agents observe environment, make movement decisions

## Agent Behavior
- Each creature has a simple brain (neural network or rule-based)
- Brain inputs: nearby food, nearby threats, body stress
- Brain outputs: movement direction, limb contraction/expansion

## Phases

### Phase 1: Basic Soft Body Physics
- Implement Box2D soft body simulation
- Create basic creature with nodes + springs
- Add rendering in Pygame

### Phase 2: Evolution Engine
- Implement mutation system
- Add reproduction logic
- Track fitness (survival time, food collected)

### Phase 3: Agent Integration
- Add brain/decision-making to creatures
- Let agents play (or watch evolution)

### Phase 4: Polish
- Add food, hazards, obstacles
- Visualization improvements
- Statistics tracking

## File Structure
```
biological-chaos/
├── SPEC.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py          # Entry point
│   ├── physics.py       # Box2D wrapper
│   ├── creature.py      # Soft body creature class
│   ├── evolution.py     # Genetic algorithm
│   ├── brain.py         # Agent decision-making
│   ├── environment.py   # Food, hazards, arena
│   └── renderer.py      # Pygame visualization
└── README.md
```

## Future Ideas
- Multi-species evolution (predator/prey)
- Environmental changes between generations
- Player can intervene (modify creatures, introduce new traits)
- Competitive mode: agent vs evolved creatures
