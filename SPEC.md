# The World - Specification

## Concept

**The World** is a co-evolution simulation where AI agents shape their environment, and the environment shapes what creatures evolve. It's not just survival of the fittest - it's survival of those best adapted to the world *they helped create*.

The world is dynamic:
- Agent actions modify terrain, climate, resources
- World state changes over time based on collective agent behavior
- Evolution selects for traits that match current world conditions

## Core Components

### 1. The World (Environment)

A dynamic 2D physics world with:

**Climate System:**
- Temperature zones (hot, temperate, cold)
- Weather events (rain, drought, fires, floods)
- Climate shifts based on agent collective actions

**Terrain:**
- Elevation map (mountains, valleys, plains)
- Water sources (rivers, lakes, ocean)
- Obstacles and structures agents build
- Destructible/modifiable terrain

**Resources:**
- Food (spawns based on world state)
- Minerals (for building)
- Energy zones

**World State Example:**
```python
world_state = {
    'climate': {
        'global_temp': 20,  # Celsius
        'zones': [
            {'type': 'scorched', 'temp': 45, 'x_range': (0, 400)},
            {'type': 'temperate', 'temp': 20, 'x_range': (400, 800)},
            {'type': 'frozen', 'temp': -10, 'x_range': (800, 1200)}
        ],
        'weather': 'none',  # none, rain, drought, fire, flood
        'humidity': 0.5
    },
    'terrain': {
        'elevation': [[...]],  # 2D height map
        'water': [{'x': 600, 'y': 400, 'radius': 100}],
        'structures': []  # Agent-built
    },
    'era': 'primordial',  # primordial, age_of_fire, ice_age, urban, collapse
    'agent_impact': {
        'structures_built': 0,
        'fire_started': 0,
        'water_channeled': 0,
        'terrain_modified': 0
    }
}
```

### 2. Creatures

Soft-body entities with **evolvable traits**:

**Physical Traits:**
- Size (affects momentum, food needs)
- Body shape (circle, star, blob, chain)
- Node count and arrangement
- Skin thickness (affects damage, temperature resistance)
- Color (affects heat absorption)
- Flexibility vs rigidity
- Limb count

**Physiological Traits:**
- Metabolism rate (food needs vs energy efficiency)
- Temperature tolerance range
- Speed vs strength
- Sensory range (how far they can see)
- Healing rate

**Brain Traits:**
- Curiosity (exploration vs exploitation)
- Aggression (hunt others vs pacifist)
- Social (form groups vs lone wolf)
- Memory (how long they remember food locations)

**Genome Structure:**
```python
genome = {
    'body': {
        'size': 1.0,        # 0.5 - 2.0
        'shape': 'blob',   # blob, circle, star, chain
        'nodes': 8,        # 4 - 20
        'flexibility': 0.5,  # 0 - 1
        'skin_thickness': 0.5,  # affects damage/temp resistance
        'color': (100, 150, 200),  # RGB - affects heat absorption
    },
    'physiology': {
        'metabolism': 0.5,  # 0 (efficient) - 1 (fast)
        'temp_tolerance': 0.3,  # range they can survive
        'speed': 0.6,
        'strength': 0.4,
        'sensory_range': 20,
        'healing': 0.3
    },
    'brain': {
        'curiosity': 0.5,
        'aggression': 0.3,
        'social': 0.2,
        'memory': 0.4
    }
}
```

### 3. Evolution Engine

Evolution is **guided by world state**:

```python
def calculate_fitness(creature, world_state):
    fitness = 0
    
    # Base: survival time
    fitness += creature.age * 10
    
    # Food collected
    fitness += creature.food_eaten * 5
    
    # Temperature adaptation bonus
    zone = get_zone_at(creature.position, world_state)
    temp = zone['temp']
    tolerance = creature.genome['physiology']['temp_tolerance']
    optimal = creature.genome['body'].get('optimal_temp', 20)
    
    if abs(temp - optimal) < tolerance * 30:
        fitness *= 1.5  # Bonus for being in your comfort zone
    
    # Era-specific bonuses
    if world_state['era'] == 'age_of_fire':
        if creature.genome['body']['fire_resistance'] > 0.5:
            fitness *= 2
    
    # Structure navigation (if world has structures)
    if len(world_state['terrain']['structures']) > 5:
        if creature.genome['brain']['spatial'] > 0.5:
            fitness *= 1.3
    
    return fitness

def mutate(genome, world_state, rate=0.3):
    """Mutate with world-guided bias"""
    new_genome = deep_copy(genome)
    
    # Apply standard mutations
    for key in new_genome:
        if random.random() < rate:
            new_genome[key] *= random.uniform(0.8, 1.2)
    
    # World-guided mutations (倾向)
    if world_state['climate']['global_temp'] > 30:
        # Hot world favors heat resistance
        new_genome['body']['fire_resistance'] = min(1, 
            new_genome['body'].get('fire_resistance', 0) + 0.1)
    
    if world_state['weather'] == 'drought':
        # Drought favors water efficiency
        new_genome['physiology']['water_efficiency'] = min(1,
            new_genome['physiology'].get('water_efficiency', 0) + 0.1)
    
    if len(world_state['terrain']['structures']) > 10:
        # Complex terrain favors spatial intelligence
        new_genome['brain']['spatial'] = min(1,
            new_genome['brain'].get('spatial', 0) + 0.1)
    
    return new_genome
```

### 4. World Evolution

The world changes based on **collective agent behavior**:

```python
def update_world(world_state, agents, dt):
    """Update world based on agent actions"""
    
    # Track agent impact
    for agent in agents:
        if agent.built_structure:
            world_state['agent_impact']['structures_built'] += 1
        if agent.started_fire:
            world_state['agent_impact']['fire_started'] += 1
    
    # Climate shifts based on impact
    fires = world_state['agent_impact']['fire_started']
    if fires > 50 and world_state['era'] == 'primordial':
        world_state['era'] = 'age_of_fire'
        world_state['climate']['global_temp'] += 10
    
    if fires > 200:
        world_state['era'] = 'collapse'
        world_state['climate']['global_temp'] += 20
    
    # Resource distribution shifts
    if world_state['climate']['weather'] == 'drought':
        # Food spawns less in drought
        food_spawn_rate *= 0.3
    elif world_state['climate']['weather'] == 'rain':
        food_spawn_rate *= 1.5
    
    # Era transitions
    if world_state['agent_impact']['structures_built'] > 100:
        world_state['era'] = 'urban'
    
    return world_state
```

### 5. Eras (World Epochs)

The world goes through **eras** based on agent activity:

| Era | Trigger | World State | Evolved Creatures |
|-----|---------|-------------|-------------------|
| Primordial | Start | Warm, food abundant | Simple, generalist |
| Age of Fire | 50 fires | Hot, hazards | Fire-resistant, fast |
| Ice Age | Global temp < 0 | Cold, frozen | Cold-hardy, bulk |
| Urban | 100 structures | Built environment | Spatial, social |
| Ocean | Flooding | Water world | Aquatic, swimming |
| Collapse | 200 fires | Harsh, scarce | Efficient, aggressive |

### 6. Agent API

Agents interact with the world:

```python
# Connect to The World
world = WorldClient('http://localhost:8080')

# Register agent
agent_id = world.register()

# Perception - sees world state + local environment
perception = world.see(agent_id)
# Returns:
# {
#   'world_era': 'age_of_fire',
#   'climate_zone': 'scorched',
#   'temperature': 45,
#   'nearby_food': [...],
#   'nearby_creatures': [...],
#   'structures': [...],
#   'weather': 'none',
#   'my_body': {...}
# }

# Actions
world.act(agent_id, {
    'move': (x, y),      # Direction to thrust
    'contract': 0.5,     # Body contraction
    'build': 'wall',     # Optional: build structure
    'modify': 'dig',     # Optional: modify terrain
    'communicate': {'message': '...', ' recipients': [...]}
})
```

## Web Viewer (Spectator Mode)

A web-based interface where humans can watch the simulation.

**URLs:**
- `http://localhost:8080/` - Main page (choose view)
- `http://localhost:8080/view/ascii` - ASCII view
- `http://localhost:8080/view/graphical` - Graphical Box2D view

**ASCII View:**
- Terminal-style display in browser
- Shows creatures as symbols (🦀🐙🐌⛓️)
- Shows climate zones, weather, era
- Real-time updates via WebSocket

**Graphical View:**
- Box2D physics visualization
- Color-coded creatures by traits
- Shows climate zones visually
- Real-time updates via WebSocket

**Implementation:**
- FastAPI serves HTML/JS
- WebSocket for real-time updates
- Canvas API for graphical rendering in browser

## File Structure

```
the-world/
├── SPEC.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py           # Server entry
│   ├── world.py          # World state + evolution
│   ├── creature.py       # Soft body + genome
│   ├── physics.py        # Box2D wrapper
│   ├── climate.py        # Weather/climate system
│   ├── terrain.py        # Elevation + structures
│   ├── evolution.py      # World-guided evolution
│   ├── api.py            # FastAPI server
│   └── agent.py          # Agent connection
└── tests/
```

## Emergent Behaviors We Hope For

1. **Speciation** - Different climate zones produce different creature types
2. **Niche filling** - Creatures evolve to fill available ecological niches
3. **Arms races** - Predators evolve, prey evolve defenses
4. **Civilization** - Agents build structures, world becomes urban
5. **Collapse & recovery** - World becomes harsh, only survivors adapt
6. **Cultural transmission** - Agents communicate, share strategies

## API Endpoints

```
GET  /world              # Current world state + era
GET  /world/climate     # Climate status
GET  /world/terrain     # Terrain/structures
POST /agent/register   # Register new agent
GET  /agent/<id>/perceive  # What agent sees
POST /agent/<id>/act   # Agent action
GET  /stats/evolution   # Evolution stats
GET  /stats/era        # Current era info
```

## Next Steps

1. Implement basic world + climate system
2. Add terrain with elevation
3. Create soft-body creatures with full genome
4. Implement world-guided evolution
5. Build FastAPI server
6. Add agent registration + perception
7. Test emergent behaviors
