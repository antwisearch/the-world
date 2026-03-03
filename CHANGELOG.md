# The World - Changelog

## Done

### Core Simulation
- [x] Box2D physics engine integration
- [x] Soft-body creatures with nodes and springs
- [x] Climate zones (scorched, temperate, frozen)
- [x] Era system (primordial → age_of_fire → ice_age → urban → collapse)
- [x] World-guided evolution (creatures adapt to world state)
- [x] Food spawning based on world conditions

### Agent API
- [x] FastAPI server
- [x] Agent registration (`/agent/register`)
- [x] Agent perception (`/agent/<id>/perceive`)
- [x] Agent actions (`/agent/<id>/act`)

### Web Viewer
- [x] HTML/CSS/JS frontend
- [x] WebSocket streaming (`/ws`)
- [x] ASCII view (terminal-style in browser)
- [x] Graphical view (Box2D rendered on canvas)
- [x] Sidebar with stats

---

## To Do

### Priority 1 - Essential
- [ ] Fix WebSocket broadcasting (currently testing)
- [ ] Add creature eating food
- [ ] Add creature collision
- [ ] Save/load simulation state

### Priority 2 - Features
- [ ] Agent communication
- [ ] Structure building (agents can modify terrain)
- [ ] Weather events (rain, drought, fire, flood)
- [ ] More creature behaviors

### Priority 3 - Polish
- [ ] Better graphical rendering
- [ ] Sound effects
- [ ] Multiple viewing angles
- [ ] Export evolution data

---

## Ideas

### Future Features
- Multi-world support (multiple simulations)
- Tournament mode (agents compete)
- Human-playable creatures
- Save/load genomes
- Cross-world trading
