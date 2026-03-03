# Biological Chaos

Soft-body creatures that evolve through natural selection based on survival. Watch evolution happen in real-time as creatures compete for food, avoid hazards, and pass on their traits to the next generation.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Box2D](https://img.shields.io/badge/Box2D-Physics-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Concept

This project simulates artificial life evolution using physics-based soft bodies. Creatures made of connected nodes compete in an arena where:

- **Physics** determines survival - size, shape, and elasticity affect movement
- **Evolution** selects for fitness - survivors reproduce with mutations
- **Intelligence** emerges - agents learn to navigate, hunt, and survive

## Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/biological-chaos.git
cd biological-chaos

# Install dependencies
pip install -r requirements.txt

# Run the simulation
python src/main.py
```

## Requirements

- Python 3.10+
- Pygame
- Box2D (via PyBox2D or similar)

See `requirements.txt` for full list.

## Documentation

See [SPEC.md](SPEC.md) for detailed specification.

## License

MIT
