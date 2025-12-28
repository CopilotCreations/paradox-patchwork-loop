# Infinite Story Loop - Architecture Documentation

## Overview

Infinite Story Loop is a surreal text adventure game that dynamically detects narrative loops and paradoxes in player choices. When contradictions or loops occur, the story rewrites itself in real-time to reconcile paradoxes, producing unpredictable and mind-bending outcomes.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INFINITE STORY LOOP                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐     │
│  │  ConsoleInterface│◄────│  GameController  │─────►│  StateManager    │     │
│  │  (Display/Input) │     │  (Coordination)  │     │  (Save/Load)     │     │
│  └─────────────────┘     └────────┬─────────┘     └──────────────────┘     │
│                                   │                                         │
│                                   ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                     InfiniteStoryLoop                              │    │
│  │  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐ │    │
│  │  │ StoryGraph   │  │ ParadoxDetection │  │   StoryGenerator     │ │    │
│  │  │ (Nodes/Edges)│  │ (Loop/Contradict)│  │   (Text Generation)  │ │    │
│  │  └──────────────┘  └──────────────────┘  └──────────────────────┘ │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                   │                                         │
│           ┌───────────────────────┼───────────────────────┐                │
│           ▼                       ▼                       ▼                │
│  ┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐     │
│  │     Player      │     │    StoryNode     │     │  HistoryTracker  │     │
│  │ (State/Inventory│     │  (Scene/Choices) │     │  (Event Logging) │     │
│  └─────────────────┘     └──────────────────┘     └──────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Story Node (`src/story_node.py`)

The fundamental building block of the narrative structure.

```python
@dataclass
class StoryNode:
    id: str                    # Unique identifier
    text: str                  # Narrative text displayed
    node_type: NodeType        # NARRATIVE, CHOICE, PARADOX, etc.
    choices: list[Choice]      # Available player choices
    previous_node_ids: list    # Links for paradox detection
    location: str              # Scene location
    is_rewritten: bool         # Paradox resolution flag
    original_text: str         # Pre-rewrite text (if any)
```

**Key Features:**
- **Immutable History**: Original text preserved when rewritten
- **Tagging System**: Nodes can be tagged for categorization
- **Serialization**: Full support for save/load operations
- **Clone Support**: Create variations of existing nodes

### 2. Story Graph (`src/story_node.py`)

Manages the complete narrative structure.

```python
class StoryGraph:
    nodes: dict[str, StoryNode]  # All story nodes
    root_id: str                  # Starting node ID
```

**Capabilities:**
- Path finding between nodes (BFS)
- Cycle detection for loop identification
- Location and tag-based queries
- Full serialization support

### 3. Player (`src/player.py`)

Tracks player state throughout the game.

```python
@dataclass
class Player:
    name: str
    inventory: list[str]
    current_location: str
    visited_locations: set[str]
    choice_history: list[str]
    action_history: list[dict]
    flags: dict[str, bool]
    variables: dict[str, any]
```

**Features:**
- Inventory management (add/remove/check items)
- Location tracking and history
- Action pattern detection (for loop identification)
- State snapshots for paradox analysis

### 4. Command Parser (`src/player.py`)

Interprets player input into structured commands.

```python
class CommandParser:
    VERBS = {
        "go": ["go", "walk", "move", "travel"],
        "take": ["take", "pick", "grab", "get"],
        "look": ["look", "examine", "inspect"],
        # ... more verb mappings
    }
```

**Parsing Flow:**
1. Tokenize input
2. Identify verb from known aliases
3. Extract target (with preposition stripping)
4. Determine if system command
5. Return structured command dict

### 5. Infinite Story Loop (`src/story_loop.py`)

The core game engine handling all narrative logic.

```python
class InfiniteStoryLoop:
    story_graph: StoryGraph
    current_node: StoryNode
    player: Player
    history: HistoryTracker
    paradox_count: int
    rewrite_count: int
```

**Main Responsibilities:**
- Process player input
- Detect paradoxes (loops, contradictions, impossible states)
- Generate dynamic story content
- Rewrite nodes to resolve paradoxes
- Maintain narrative continuity

### 6. Story Generator (`src/story_loop.py`)

Generates dynamic narrative content.

```python
class StoryGenerator:
    TEMPLATES = {
        "intro": [...],
        "paradox_resolution": [...],
        "loop_break": [...],
        "location_descriptions": {...},
    }
    CHARACTERS = {...}
```

**Generation Types:**
- Location introductions
- Paradox resolution text
- Loop break narratives
- Dynamic choices based on context
- Surreal event injection

### 7. History Tracker (`src/utils.py`)

Tracks game events for paradox detection.

```python
class HistoryTracker:
    entries: list[HistoryEntry]
    state_hashes: set[str]
    contradiction_rules: list[dict]
```

**Detection Capabilities:**
- State loop detection (via hashing)
- Node visit pattern loops
- Contradiction detection (configurable rules)

### 8. State Manager (`src/utils.py`)

Handles game persistence.

```python
class StateManager:
    save_directory: Path
    auto_save_enabled: bool
    auto_save_interval: int
```

**Features:**
- Manual save/load
- Auto-save at configurable intervals
- Save file listing and deletion
- JSON-based storage format

## Data Flow

### Input Processing

```
User Input
    │
    ▼
CommandParser.parse()
    │
    ├─── System Command ──► Handle directly (help, status, quit)
    │
    └─── Game Action
            │
            ▼
    InfiniteStoryLoop._detect_paradox()
            │
            ├─── Paradox Found ──► _handle_paradox() ──► Generate resolution
            │
            └─── No Paradox ──► _advance_story() ──► Generate next node
                                    │
                                    ▼
                            Display response to player
```

### Paradox Detection Flow

```
Current Action + History
        │
        ▼
┌───────────────────────────┐
│   Check Action Loops      │ ◄─── Player.detect_action_loop()
│   (Repeating patterns)    │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│   Check Node Loops        │ ◄─── HistoryTracker.detect_node_loop()
│   (Visiting same nodes)   │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│   Check Contradictions    │ ◄─── HistoryTracker.detect_contradiction()
│   (Conflicting actions)   │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│   Check Impossible States │ ◄─── Using items not in inventory
│   (Invalid game states)   │
└───────────┴───────────────┘
            │
            ▼
    Paradox Object (or None)
```

### Story Generation Flow

```
Player Command
    │
    ▼
Determine New Location
    │
    ▼
Generate Story Text (from templates + context)
    │
    ▼
Create StoryNode
    │
    ▼
Generate Choices (based on location + player state)
    │
    ▼
Potentially Grant Items (random chance)
    │
    ▼
Update Story Graph
    │
    ▼
Record in History
    │
    ▼
Return Response
```

## Paradox Types

| Type | Description | Detection Method |
|------|-------------|------------------|
| TEMPORAL_LOOP | Player stuck in repeating actions | Pattern matching on action history |
| CONTRADICTION | Conflicting actions | Rule-based matching (take/drop, open/close) |
| IMPOSSIBLE_STATE | Invalid game state | State validation (using non-existent items) |
| NARRATIVE_BREAK | Story continuity broken | Node reference validation |
| CAUSAL_PARADOX | Cause and effect reversed | Sequence analysis |

## Serialization Format

### Game State JSON Structure

```json
{
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00",
  "game_state": {
    "story_graph": {
      "nodes": {
        "node-id-1": {
          "id": "node-id-1",
          "text": "Story text...",
          "node_type": "NARRATIVE",
          "choices": [...],
          "location": "the beginning"
        }
      },
      "root_id": "node-id-1"
    },
    "current_node_id": "node-id-1",
    "player": {
      "name": "Traveler",
      "inventory": ["key", "map"],
      "current_location": "the library",
      "visited_locations": ["the beginning", "the library"],
      "choice_history": ["node-1", "node-2"],
      "flags": {"met_keeper": true},
      "variables": {"paradox_encounters": 3}
    },
    "history": {
      "entries": [...],
      "state_hashes": ["abc123", "def456"]
    },
    "paradox_count": 2,
    "rewrite_count": 1
  }
}
```

## Extension Points

### Adding New Locations

```python
# In StoryGenerator.TEMPLATES["location_descriptions"]
"new_location": "description of the new location"
```

### Adding New Paradox Rules

```python
# In HistoryTracker._setup_default_rules()
self.contradiction_rules.append({
    "action1": "verb1",
    "action2": "verb2",
    "same_target": True,  # or "sequence": True
})
```

### Adding New Story Templates

```python
# In StoryGenerator.TEMPLATES
"new_category": [
    "Template with {placeholder}...",
    "Another variation...",
]
```

## Performance Considerations

1. **State Hashing**: Uses MD5 for quick state comparison
2. **History Limiting**: Paradox detection checks only recent entries (last 20)
3. **Lazy Graph Building**: Nodes created on-demand as player explores
4. **Efficient Serialization**: JSON with only necessary data

## Testing Strategy

- **Unit Tests**: Each module tested independently
- **Integration Tests**: Component interaction testing
- **Coverage Goal**: Minimum 75% code coverage
- **CI/CD**: Automated testing on multiple Python versions and OS platforms
