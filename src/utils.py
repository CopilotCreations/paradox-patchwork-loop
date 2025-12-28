"""
Utilities Module - Helper functions for logging, history, and state management.

This module provides utility classes and functions for:
- Game logging with timestamps
- History tracking for paradox detection
- Save/load game state functionality
"""

from __future__ import annotations
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field
import hashlib


class GameLogger:
    """
    Handles game logging with timestamps and categories.
    
    Provides methods for logging game events, debug information,
    and creating a readable game log file.
    
    Attributes:
        log_file: Path to the log file
        console_output: Whether to also print to console
        log_level: Minimum level to log
    """
    
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "STORY": 25,  # Custom level for story events
    }
    
    def __init__(
        self,
        log_file: Optional[str] = None,
        console_output: bool = False,
        log_level: str = "INFO"
    ):
        """
        Initialize the game logger.
        
        Args:
            log_file: Path to log file (None for no file logging)
            console_output: Whether to print logs to console
            log_level: Minimum level to log
        """
        self.log_file = log_file
        self.console_output = console_output
        self.log_level = self.LEVELS.get(log_level.upper(), 20)
        self.entries: list[dict] = []
        
        if log_file:
            self._setup_file_logging()
    
    def _setup_file_logging(self) -> None:
        """Set up file logging."""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _format_entry(self, entry: dict) -> str:
        """Format a log entry as a string."""
        timestamp = entry["timestamp"]
        level = entry["level"]
        category = entry.get("category", "GENERAL")
        message = entry["message"]
        return f"[{timestamp}] [{level}] [{category}] {message}"
    
    def log(
        self,
        message: str,
        level: str = "INFO",
        category: str = "GENERAL"
    ) -> None:
        """
        Log a message.
        
        Args:
            message: The message to log
            level: Log level (DEBUG, INFO, WARNING, ERROR, STORY)
            category: Category for the log entry
        """
        level_value = self.LEVELS.get(level.upper(), 20)
        if level_value < self.log_level:
            return
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "category": category,
            "message": message,
        }
        
        self.entries.append(entry)
        
        formatted = self._format_entry(entry)
        
        if self.console_output:
            print(formatted)
        
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
    
    def debug(self, message: str, category: str = "DEBUG") -> None:
        """Log a debug message."""
        self.log(message, "DEBUG", category)
    
    def info(self, message: str, category: str = "GENERAL") -> None:
        """Log an info message."""
        self.log(message, "INFO", category)
    
    def warning(self, message: str, category: str = "GENERAL") -> None:
        """Log a warning message."""
        self.log(message, "WARNING", category)
    
    def error(self, message: str, category: str = "ERROR") -> None:
        """Log an error message."""
        self.log(message, "ERROR", category)
    
    def story(self, message: str) -> None:
        """Log a story event."""
        self.log(message, "STORY", "NARRATIVE")
    
    def paradox(self, message: str) -> None:
        """Log a paradox event."""
        self.log(message, "WARNING", "PARADOX")
    
    def get_entries(
        self,
        level: Optional[str] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[dict]:
        """
        Get log entries with optional filters.
        
        Args:
            level: Filter by level
            category: Filter by category
            limit: Maximum number of entries to return
            
        Returns:
            List of matching log entries
        """
        result = self.entries
        
        if level:
            result = [e for e in result if e["level"] == level.upper()]
        
        if category:
            result = [e for e in result if e["category"] == category.upper()]
        
        if limit:
            result = result[-limit:]
        
        return result
    
    def clear(self) -> None:
        """Clear all log entries."""
        self.entries = []


@dataclass
class HistoryEntry:
    """
    Represents a single entry in the game history.
    
    Attributes:
        node_id: ID of the story node
        action: The action taken
        timestamp: When this entry was created
        state_hash: Hash of the game state at this point
        metadata: Additional information about this entry
    """
    
    node_id: str
    action: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    state_hash: str = ""
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "action": self.action,
            "timestamp": self.timestamp,
            "state_hash": self.state_hash,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HistoryEntry':
        """Create from dictionary."""
        return cls(
            node_id=data.get("node_id", ""),
            action=data.get("action", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            state_hash=data.get("state_hash", ""),
            metadata=data.get("metadata", {}),
        )


class HistoryTracker:
    """
    Tracks the complete history of game events for paradox detection.
    
    Maintains a record of all story nodes visited, actions taken,
    and state changes. Provides methods for detecting loops and
    contradictions in the narrative.
    
    Attributes:
        entries: List of history entries
        state_hashes: Set of seen state hashes (for loop detection)
        contradiction_rules: List of rules for detecting contradictions
    """
    
    def __init__(self):
        """Initialize the history tracker."""
        self.entries: list[HistoryEntry] = []
        self.state_hashes: set[str] = set()
        self.contradiction_rules: list[dict] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self) -> None:
        """Set up default contradiction detection rules."""
        # These rules define action pairs that contradict each other
        self.contradiction_rules = [
            {"action1": "take", "action2": "drop", "same_target": True},
            {"action1": "open", "action2": "close", "same_target": True},
            {"action1": "go north", "action2": "go south", "sequence": True},
            {"action1": "go east", "action2": "go west", "sequence": True},
            {"action1": "attack", "action2": "talk", "same_target": True},
        ]
    
    def add_entry(
        self,
        node_id: str,
        action: str,
        state: dict,
        metadata: Optional[dict] = None
    ) -> HistoryEntry:
        """
        Add an entry to the history.
        
        Args:
            node_id: ID of the current story node
            action: The action taken
            state: Current game state for hashing
            metadata: Additional metadata
            
        Returns:
            The created HistoryEntry
        """
        state_hash = self._hash_state(state)
        
        entry = HistoryEntry(
            node_id=node_id,
            action=action,
            state_hash=state_hash,
            metadata=metadata or {},
        )
        
        self.entries.append(entry)
        self.state_hashes.add(state_hash)
        
        return entry
    
    def _hash_state(self, state: dict) -> str:
        """
        Create a hash of the game state.
        
        Args:
            state: Game state dictionary
            
        Returns:
            MD5 hash of the state
        """
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.md5(state_str.encode()).hexdigest()
    
    def detect_loop(self, current_state: dict) -> Optional[int]:
        """
        Detect if the current state creates a loop.
        
        Args:
            current_state: Current game state
            
        Returns:
            Index of the matching previous state, or None
        """
        current_hash = self._hash_state(current_state)
        
        if current_hash in self.state_hashes:
            # Find which entry has this hash
            for i, entry in enumerate(self.entries):
                if entry.state_hash == current_hash:
                    return i
        
        return None
    
    def detect_node_loop(self, window_size: int = 10) -> Optional[list[str]]:
        """
        Detect if recent node visits form a loop.
        
        Args:
            window_size: Number of recent entries to check
            
        Returns:
            List of node IDs forming the loop, or None
        """
        if len(self.entries) < window_size:
            return None
        
        recent_nodes = [e.node_id for e in self.entries[-window_size:]]
        
        # Check for repeating patterns
        for pattern_length in range(2, window_size // 2 + 1):
            pattern = recent_nodes[-pattern_length:]
            previous = recent_nodes[-pattern_length * 2:-pattern_length]
            
            if pattern == previous:
                return pattern
        
        return None
    
    def detect_contradiction(
        self,
        action: str,
        target: Optional[str] = None
    ) -> Optional[dict]:
        """
        Detect if an action contradicts a previous action.
        
        Args:
            action: The action being taken
            target: The target of the action
            
        Returns:
            Dict describing the contradiction, or None
        """
        action_lower = action.lower()
        target_lower = target.lower() if target else ""
        
        for rule in self.contradiction_rules:
            action1 = rule["action1"]
            action2 = rule["action2"]
            
            # Check if current action matches either side
            if action_lower.startswith(action1) or action_lower.startswith(action2):
                # Look for contradicting action in history
                for entry in reversed(self.entries[-20:]):  # Check last 20 entries
                    prev_action = entry.action.lower()
                    prev_target_raw = entry.metadata.get("target", "") if entry.metadata else ""
                    prev_target = prev_target_raw.lower() if prev_target_raw else ""
                    
                    # Check for matching contradiction
                    is_match = False
                    if action_lower.startswith(action1) and prev_action.startswith(action2):
                        is_match = True
                    elif action_lower.startswith(action2) and prev_action.startswith(action1):
                        is_match = True
                    
                    if is_match:
                        # Check additional conditions
                        if rule.get("same_target") and target_lower and prev_target:
                            if target_lower == prev_target:
                                return {
                                    "type": "contradiction",
                                    "current_action": action,
                                    "previous_action": entry.action,
                                    "target": target,
                                    "rule": rule,
                                }
                        elif rule.get("sequence"):
                            return {
                                "type": "sequence_contradiction",
                                "current_action": action,
                                "previous_action": entry.action,
                                "rule": rule,
                            }
        
        return None
    
    def get_recent_actions(self, count: int = 10) -> list[str]:
        """
        Get the most recent actions.
        
        Args:
            count: Number of actions to return
            
        Returns:
            List of recent action strings
        """
        return [e.action for e in self.entries[-count:]]
    
    def get_visited_nodes(self) -> set[str]:
        """Get set of all visited node IDs."""
        return {e.node_id for e in self.entries}
    
    def get_node_visit_count(self, node_id: str) -> int:
        """Get number of times a node was visited."""
        return sum(1 for e in self.entries if e.node_id == node_id)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "entries": [e.to_dict() for e in self.entries],
            "state_hashes": list(self.state_hashes),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HistoryTracker':
        """Create from dictionary."""
        tracker = cls()
        tracker.entries = [
            HistoryEntry.from_dict(e) for e in data.get("entries", [])
        ]
        tracker.state_hashes = set(data.get("state_hashes", []))
        return tracker
    
    def clear(self) -> None:
        """Clear all history."""
        self.entries = []
        self.state_hashes = set()


class StateManager:
    """
    Manages saving and loading of game state.
    
    Provides methods for serializing the complete game state
    to JSON files and restoring from saved files.
    
    Attributes:
        save_directory: Directory for save files
        auto_save_enabled: Whether auto-save is enabled
        auto_save_interval: Number of actions between auto-saves
    """
    
    def __init__(
        self,
        save_directory: str = "saves",
        auto_save_enabled: bool = True,
        auto_save_interval: int = 10
    ):
        """
        Initialize the state manager.
        
        Args:
            save_directory: Directory for save files
            auto_save_enabled: Whether to enable auto-save
            auto_save_interval: Actions between auto-saves
        """
        self.save_directory = Path(save_directory)
        self.auto_save_enabled = auto_save_enabled
        self.auto_save_interval = auto_save_interval
        self.action_count = 0
    
    def _ensure_save_directory(self) -> None:
        """Ensure the save directory exists."""
        self.save_directory.mkdir(parents=True, exist_ok=True)
    
    def save(
        self,
        game_state: dict,
        filename: Optional[str] = None
    ) -> str:
        """
        Save game state to a file.
        
        Args:
            game_state: Dictionary containing complete game state
            filename: Name for the save file (auto-generated if None)
            
        Returns:
            Path to the saved file
        """
        self._ensure_save_directory()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.json"
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        save_path = self.save_directory / filename
        
        # Add metadata to save
        save_data = {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "game_state": game_state,
        }
        
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        return str(save_path)
    
    def load(self, filename: str) -> Optional[dict]:
        """
        Load game state from a file.
        
        Args:
            filename: Name of the save file to load
            
        Returns:
            Game state dictionary, or None if load failed
        """
        if not filename.endswith(".json"):
            filename += ".json"
        
        save_path = self.save_directory / filename
        
        if not save_path.exists():
            return None
        
        try:
            with open(save_path, "r", encoding="utf-8") as f:
                save_data = json.load(f)
            
            return save_data.get("game_state")
        except (json.JSONDecodeError, IOError):
            return None
    
    def list_saves(self) -> list[dict]:
        """
        List all available save files.
        
        Returns:
            List of dicts with save file info
        """
        self._ensure_save_directory()
        
        saves = []
        for save_file in self.save_directory.glob("*.json"):
            try:
                with open(save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                saves.append({
                    "filename": save_file.name,
                    "timestamp": data.get("timestamp", "unknown"),
                    "version": data.get("version", "unknown"),
                })
            except (json.JSONDecodeError, IOError):
                continue
        
        return sorted(saves, key=lambda x: x["timestamp"], reverse=True)
    
    def delete_save(self, filename: str) -> bool:
        """
        Delete a save file.
        
        Args:
            filename: Name of the save file to delete
            
        Returns:
            True if deleted, False otherwise
        """
        if not filename.endswith(".json"):
            filename += ".json"
        
        save_path = self.save_directory / filename
        
        if save_path.exists():
            save_path.unlink()
            return True
        
        return False
    
    def auto_save(self, game_state: dict) -> Optional[str]:
        """
        Perform auto-save if conditions are met.
        
        Args:
            game_state: Current game state
            
        Returns:
            Path to save file if saved, None otherwise
        """
        self.action_count += 1
        
        if not self.auto_save_enabled:
            return None
        
        if self.action_count % self.auto_save_interval == 0:
            return self.save(game_state, "autosave")
        
        return None


def format_story_text(text: str, width: int = 70) -> str:
    """
    Format story text for console display.
    
    Wraps text to specified width while preserving paragraph breaks.
    
    Args:
        text: The text to format
        width: Maximum line width
        
    Returns:
        Formatted text string
    """
    import textwrap
    
    paragraphs = text.split("\n\n")
    formatted_paragraphs = []
    
    for para in paragraphs:
        # Normalize whitespace within paragraph
        para = " ".join(para.split())
        # Wrap to width
        wrapped = textwrap.fill(para, width=width)
        formatted_paragraphs.append(wrapped)
    
    return "\n\n".join(formatted_paragraphs)


def create_separator(char: str = "═", width: int = 70) -> str:
    """
    Create a separator line for console display.
    
    Args:
        char: Character to use for the separator
        width: Width of the separator
        
    Returns:
        Separator string
    """
    return char * width


def create_header(text: str, width: int = 70, char: str = "═") -> str:
    """
    Create a centered header with decorative borders.
    
    Args:
        text: Header text
        width: Total width
        char: Border character
        
    Returns:
        Formatted header string
    """
    padding = (width - len(text) - 4) // 2
    return f"╔{char * (width - 2)}╗\n║{' ' * padding} {text} {' ' * padding}║\n╚{char * (width - 2)}╝"


def get_random_surreal_event() -> str:
    """
    Get a random surreal event description.
    
    Used when paradoxes or loops are detected to inject
    unexpected narrative elements.
    
    Returns:
        A surreal event description string
    """
    import random
    
    events = [
        "The walls begin to whisper your previous choices back to you.",
        "A clock runs backwards, erasing moments that never existed.",
        "Your shadow steps forward and takes your place momentarily.",
        "The ground becomes the ceiling, and you realize you've always been falling upward.",
        "A door appears where there was none, labeled 'This Way to Yesterday'.",
        "The colors in the room swap places, and suddenly blue tastes like Wednesday.",
        "A previous version of yourself walks past, ignoring your existence.",
        "The narrative hiccups, and for a moment, you exist in two places at once.",
        "Time folds like origami, and you catch a glimpse of all possible outcomes.",
        "The story pauses to catch its breath, and you hear the author's pen scratching.",
        "Reality buffering... please wait while the universe recalculates.",
        "A footnote appears in mid-air: *This event may or may not have happened.*",
        "The scenery flickers like a candle, revealing the stage behind the world.",
        "Your inventory temporarily includes 'one existential crisis' before vanishing.",
        "The ground remembers being sky and becomes confused about its purpose.",
    ]
    
    return random.choice(events)


def parse_freeform_input(text: str) -> dict:
    """
    Attempt to extract meaningful actions from freeform text.
    
    Uses keyword matching and pattern recognition to interpret
    the player's intent from natural language input.
    
    Args:
        text: The freeform input text
        
    Returns:
        Dict with extracted verb, target, and confidence
    """
    import re
    
    text_lower = text.lower().strip()
    
    # Pattern matching for common structures
    patterns = [
        (r"i (?:want to |will |shall |would like to )?(\w+)(?: the | a | an )?(.+)?", 0.8),
        (r"(?:can i |could i |let me )?(\w+)(?: the | a | an )?(.+)?", 0.7),
        (r"(\w+)(?: the | a | an )?(.+)", 0.5),
    ]
    
    for pattern, confidence in patterns:
        match = re.match(pattern, text_lower)
        if match:
            verb = match.group(1)
            target = match.group(2) if match.lastindex >= 2 else None
            return {
                "verb": verb,
                "target": target.strip() if target else None,
                "confidence": confidence,
            }
    
    return {
        "verb": None,
        "target": None,
        "confidence": 0.0,
    }
