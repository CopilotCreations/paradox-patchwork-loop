# Infinite Story Loop - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Game Commands](#game-commands)
5. [Gameplay Tips](#gameplay-tips)
6. [Understanding Paradoxes](#understanding-paradoxes)
7. [Save and Load](#save-and-load)
8. [Troubleshooting](#troubleshooting)

## Introduction

**Infinite Story Loop** is a surreal text adventure where your choices shape an ever-evolving narrative. Unlike traditional text adventures, this game features:

- **Dynamic Paradox Detection**: The game recognizes when your actions contradict previous choices or create narrative loops
- **Real-time Story Rewriting**: When paradoxes occur, the story rewrites itself to maintain coherence
- **Surreal Events**: Expect the unexpected—reality itself bends to accommodate your journey
- **Emergent Narrative**: Each playthrough is unique as the story adapts to your choices

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Steps

1. **Clone or download the project**
   ```bash
   cd paradox-patchwork-loop
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game**
   ```bash
   python run.py
   ```

## Quick Start

When you start the game, you'll see the title screen and be placed in "the beginning"—an endless white expanse where stories are born.

```
═══════════════════════════════════════════════════════════════════════

You find yourself in an endless white expanse where stories are born.
The air feels thick with possibility, as if reality itself is waiting
to see what you'll do next.

What do you do?

  [1] Walk towards the light
  [2] Follow the shadows
  [3] Listen to the whispers
  [4] Question your existence

> 
```

Simply type your command and press Enter. You can:
- Type the choice number (e.g., `1`)
- Type the action directly (e.g., `go north`)
- Use natural language (e.g., `I want to explore`)

## Game Commands

### Movement Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `go north` | `n`, `north`, `walk north` | Move northward |
| `go south` | `s`, `south`, `walk south` | Move southward |
| `go east` | `e`, `east`, `walk east` | Move eastward |
| `go west` | `w`, `west`, `walk west` | Move westward |

### Action Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `look` | `examine`, `inspect` | Examine your surroundings |
| `take [item]` | `pick up`, `grab`, `get` | Pick up an item |
| `drop [item]` | `put down`, `leave` | Drop an item |
| `use [item]` | `activate`, `operate` | Use an item |
| `talk [target]` | `speak to`, `ask` | Talk to someone/something |

### System Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `help` | `?`, `commands` | Show help information |
| `status` | `inventory`, `inv`, `i` | Show your status and inventory |
| `map` | `history` | View your story path and statistics |
| `save` | - | Save your current game |
| `load` | `restore` | Load a saved game |
| `quit` | `exit`, `q` | Exit the game |

### Example Session

```
> look

══════════════════════════════════════════════════════════════════════

You examine your surroundings carefully. Towering shelves of unwritten
books stretch into infinity. Everything seems both familiar and strange.

What do you do?

  [1] Go north
  [2] Go south
  [3] Go east
  [4] Read a book
  [5] Look around

> take mysterious book

══════════════════════════════════════════════════════════════════════

You reach for the mysterious book. It feels significant in your hands.
Reality seems to acknowledge your choice.

You notice something interesting and pick it up.

What do you do?
...
```

## Gameplay Tips

### 1. Embrace the Surreal

The game intentionally creates bizarre and unexpected situations. Don't fight it—lean into the strangeness:

```
The ground becomes the ceiling, and you realize you've always been falling upward.
```

### 2. Experiment with Actions

Try different commands, even nonsensical ones. The game interprets freeform input:

```
> I want to dance with the shadows
> tell the walls my secrets
> become one with the narrative
```

### 3. Create Paradoxes (Intentionally)

Some of the most interesting story moments occur when you create contradictions:

```
> take the sword
> drop the sword
> take the sword
> drop the sword
```

This might trigger a paradox resolution that rewrites reality!

### 4. Check Your Status Often

Use `status` or `i` to track your inventory and progress:

```
╔════════════════════════════════════════╗
║ Player: Traveler                       ║
║ Location: the library                  ║
╠════════════════════════════════════════╣
║ Inventory:                             ║
║   • strange key                        ║
║   • glowing orb                        ║
╠════════════════════════════════════════╣
║ Locations visited: 5                   ║
║ Choices made: 12                       ║
╚════════════════════════════════════════╝
```

### 5. Use the Map Command

Track your journey and see statistics about paradoxes:

```
╔══════════════════════════════════════════════════════════════════════╗
║                         STORY MAP                                    ║
╠══════════════════════════════════════════════════════════════════════╣
║ VISITED LOCATIONS:                                                   ║
║  → the library                                                       ║
║    the beginning                                                     ║
║    the crossroads                                                    ║
╠══════════════════════════════════════════════════════════════════════╣
║ STATISTICS:                                                          ║
║   Choices made: 15                                                   ║
║   Paradoxes encountered: 3                                           ║
║   Story rewrites: 2                                                  ║
║   Story nodes created: 18                                            ║
╚══════════════════════════════════════════════════════════════════════╝
```

## Understanding Paradoxes

### What is a Paradox?

In Infinite Story Loop, a paradox occurs when your actions create a logical impossibility in the narrative. The game detects these and rewrites the story to maintain coherence.

### Types of Paradoxes

#### 1. Temporal Loops
Detected when you repeat the same sequence of actions multiple times:

```
╔════════════════════════════════════════╗
║        ⚠ PARADOX DETECTED ⚠           ║
╠════════════════════════════════════════╣
║  Type: TEMPORAL_LOOP                   ║
║  Severity: [██████░░░░]                ║
║  Reality is being rewritten...         ║
╚════════════════════════════════════════╝

The narrative recognizes the pattern and rebels. A new thread weaves 
itself into existence, breaking the cycle.
```

#### 2. Contradictions
Detected when you perform conflicting actions:

```
> take sword
You pick up the gleaming sword.

> drop sword
You set down the sword.

> take sword
You pick up the sword again.

> attack with sword (while you just dropped it)

╔════════════════════════════════════════╗
║        ⚠ PARADOX DETECTED ⚠           ║
╠════════════════════════════════════════╣
║  Type: CONTRADICTION                   ║
║  Severity: [████████░░]                ║
║  Reality is being rewritten...         ║
╚════════════════════════════════════════╝
```

#### 3. Impossible States
Detected when you try to use something you don't have:

```
> use magic wand

You try to use magic wand, but you don't have it... or do you?

Reality shudders and rewrites itself...
```

### After a Paradox

When a paradox is resolved, you'll typically have new choices:

- **Accept the new reality**: Continue with the rewritten narrative
- **Question what happened**: Explore the nature of the paradox
- **Try to break the cycle**: (For loops) Attempt a different path
- **Embrace the contradiction**: (For contradictions) Accept both truths

## Save and Load

### Saving Your Game

Type `save` to save your current progress:

```
> save

✓ Game saved to: saves/manual_save.json
```

### Loading a Game

Type `load` to see available saves:

```
> load

Available saves:
  [1] autosave.json (2024-01-15T10:30:00)
  [2] manual_save.json (2024-01-15T09:15:00)

Enter save number (or 'cancel'): 1

✓ Game loaded successfully!
```

### Auto-Save

The game automatically saves your progress every 10 actions. The auto-save file is named `autosave.json`.

## Troubleshooting

### Game Won't Start

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Make sure you're running from the project root directory:
```bash
cd paradox-patchwork-loop
python run.py
```

### Tests Failing

**Error**: Tests fail with import errors

**Solution**: Install test dependencies:
```bash
pip install pytest pytest-cov
```

### Save Files Not Found

**Issue**: `load` command shows no saves

**Solution**: Saves are stored in the `saves/` directory. If this directory doesn't exist, it will be created on first save.

### Display Issues

**Issue**: ASCII art or borders display incorrectly

**Solution**: Ensure your terminal supports UTF-8 encoding. On Windows, you may need to:
```bash
chcp 65001
```

### Paradox Not Triggering

**Issue**: Contradictory actions don't trigger paradoxes

**Explanation**: Not all contradictions trigger paradoxes. The game uses specific rules to detect meaningful contradictions. Try:
- Repeating the same action sequence 5+ times
- Taking and dropping the same item multiple times in a row
- Going north then immediately south multiple times

## Credits

**Infinite Story Loop** - A surreal text adventure exploring the boundaries between player and narrative.

Created as a demonstration of dynamic storytelling and paradox detection in interactive fiction.
