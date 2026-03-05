---
layout: default
title: Contributing
---

# Contributing

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install dependencies

```bash
git clone https://github.com/YOUR_USERNAME/the-world.git
cd the-world
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
python -m src.api
```

Open http://localhost:8080

## Making Changes

1. Create a branch
2. Make changes
3. Test locally
4. Submit PR

```bash
git checkout -b my-feature
# Make changes...
python -m src.api
# Test...
git add .
git commit -m "Add feature X"
git push origin my-feature
```

## Code Style

- Use meaningful variable names
- Comment complex logic
- Keep functions focused
- Add docstrings to new modules

## Adding Features

### New Jobs

Add to `jobs.py`:
```python
class NewJob:
    name = "newjob"
    
    @classmethod
    def do_job(cls, agent, world):
        # Job logic
        pass
```

### New Events

Add to `events.py`:
```python
class NewEvent(Event):
    name = "new_event"
    
    @classmethod
    def apply(cls, world):
        # Event logic
        pass
```

### New Biomes

Add to `terrain.py`:
```python
class Biome:
    NEWBIOME = 'newbiome'
```

Then update `BIOME_RESOURCES` in `biomes.py`.

## Testing

Test locally before submitting:
- Run the server
- Check /world endpoint
- Verify agents are working
- Check for errors

## Submitting PR

- Clear commit messages
- Describe what you changed
- Explain why
- Link any issues
