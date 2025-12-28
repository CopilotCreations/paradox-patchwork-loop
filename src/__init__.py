"""
Infinite Story Loop - A surreal text adventure with paradox detection.

This package contains the core game engine for the Infinite Story Loop,
a console-based text adventure that dynamically detects and resolves
narrative paradoxes and loops in real-time.
"""

__version__ = "1.0.0"
__author__ = "Infinite Story Loop Team"

from .story_node import StoryNode
from .story_loop import InfiniteStoryLoop
from .player import Player
from .utils import GameLogger, StateManager, HistoryTracker

__all__ = [
    "StoryNode",
    "InfiniteStoryLoop",
    "Player",
    "GameLogger",
    "StateManager",
    "HistoryTracker",
]
