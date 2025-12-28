# Infinite Story Loop

A surreal text adventure that dynamically detects narrative loops and paradoxes in player choices. When a contradiction or loop occurs, the story rewrites itself in real-time to reconcile the paradox, producing unpredictable, mind-bending, and sometimes humorous outcomes.

## Features

- **Dynamic Paradox Detection**: Recognizes contradictory actions, temporal loops, and impossible states
- **Real-time Story Rewriting**: The narrative adapts to resolve paradoxes while maintaining immersion
- **Surreal Event Injection**: Random surreal events add unexpected twists to the experience
- **Save/Load System**: Persist your progress with manual saves and auto-save
- **Story Map**: Track your journey and view statistics about your playthrough

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python run.py
```

## Commands

| Command | Description |
|---------|-------------|
| `go [direction]` | Move in a direction (north, south, east, west) |
| `look` | Examine your surroundings |
| `take [item]` | Pick up an item |
| `talk [target]` | Talk to someone or something |
| `status` / `i` | View your status and inventory |
| `help` / `?` | Show help information |
| `map` | View story history and statistics |
| `save` | Save your game |
| `load` | Load a saved game |
| `quit` / `q` | Exit the game |

## Project Structure

```
paradox-patchwork-loop/
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment configuration
├── .gitignore             # Git ignore patterns
│
├── src/                   # Source code
│   ├── __init__.py
│   ├── main.py           # Game loop and console interface
│   ├── story_loop.py     # Core story engine and paradox detection
│   ├── story_node.py     # Story node and graph structures
│   ├── player.py         # Player state and command parsing
│   └── utils.py          # Logging, history, and state management
│
├── tests/                 # Unit tests
│   ├── __init__.py
│   ├── test_story_node.py
│   ├── test_story_loop.py
│   ├── test_player.py
│   ├── test_utils.py
│   └── test_main.py
│
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md   # System architecture details
│   ├── USAGE.md          # User guide
│   └── SUGGESTIONS.md    # Future improvement ideas
│
└── .github/workflows/     # CI/CD pipeline
    └── ci.yml
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_story_loop.py
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and component details
- [Usage Guide](docs/USAGE.md) - How to play the game
- [Suggestions](docs/SUGGESTIONS.md) - Ideas for future development

## Requirements

- Python 3.9+
- pytest (for testing)
- pytest-cov (for coverage reports)

## License

MIT License
