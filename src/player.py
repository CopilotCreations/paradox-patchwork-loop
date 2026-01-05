"""
Player Module - Handles player state, input, and actions.

This module contains the Player class which tracks the player's
inventory, location history, choices made, and provides methods
for parsing and handling player input.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class PlayerState:
    """
    Immutable snapshot of player state for history tracking.
    
    Attributes:
        location: Current location name
        inventory: Copy of inventory at this state
        visited_locations: Set of visited locations
        choice_count: Number of choices made
    """
    
    location: str
    inventory: list[str]
    visited_locations: set[str]
    choice_count: int
    
    def to_dict(self) -> dict:
        """Convert state to dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the player state.
        """
        return {
            "location": self.location,
            "inventory": self.inventory.copy(),
            "visited_locations": list(self.visited_locations),
            "choice_count": self.choice_count,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerState':
        """Create PlayerState from dictionary.
        
        Args:
            data: Dictionary containing player state data.
            
        Returns:
            PlayerState: A new PlayerState instance.
        """
        return cls(
            location=data.get("location", "unknown"),
            inventory=data.get("inventory", []),
            visited_locations=set(data.get("visited_locations", [])),
            choice_count=data.get("choice_count", 0),
        )


class CommandParser:
    """
    Parses player input into structured commands.
    
    Supports various command formats:
    - Simple verbs: "look", "help", "quit"
    - Verb + noun: "take key", "drop sword"
    - Verb + preposition + noun: "go to north", "talk to wizard"
    - Freeform text: interpreted contextually
    """
    
    # Common action verbs and their aliases
    VERBS = {
        "go": ["go", "walk", "move", "travel", "head"],
        "take": ["take", "pick", "grab", "get", "collect"],
        "drop": ["drop", "put", "leave", "discard"],
        "look": ["look", "examine", "inspect", "observe", "see"],
        "talk": ["talk", "speak", "ask", "tell", "say"],
        "use": ["use", "activate", "operate", "interact"],
        "open": ["open", "unlock"],
        "close": ["close", "shut", "lock"],
        "attack": ["attack", "fight", "hit", "strike"],
        "help": ["help", "?", "commands"],
        "status": ["status", "inventory", "inv", "i"],
        "quit": ["quit", "exit", "q"],
        "save": ["save"],
        "load": ["load", "restore"],
        "map": ["map", "history"],
    }
    
    # Prepositions to strip
    PREPOSITIONS = ["to", "at", "with", "on", "in", "from", "the", "a", "an"]
    
    @classmethod
    def parse(cls, input_text: str) -> dict:
        """
        Parse player input into a structured command.
        
        Args:
            input_text: Raw input from the player
            
        Returns:
            Dictionary with 'verb', 'target', 'original', and 'is_command' keys
        """
        original = input_text.strip()
        cleaned = original.lower()
        
        if not cleaned:
            return {
                "verb": None,
                "target": None,
                "original": original,
                "is_command": False,
            }
        
        # Split into words
        words = cleaned.split()
        
        # Find the verb
        verb = None
        verb_index = 0
        
        for i, word in enumerate(words):
            for canonical, aliases in cls.VERBS.items():
                if word in aliases:
                    verb = canonical
                    verb_index = i
                    break
            if verb:
                break
        
        # Extract target (everything after verb, minus prepositions)
        target = None
        if verb and verb_index < len(words) - 1:
            target_words = words[verb_index + 1:]
            # Remove leading prepositions
            while target_words and target_words[0] in cls.PREPOSITIONS:
                target_words.pop(0)
            if target_words:
                target = " ".join(target_words)
        
        # Check if this is a system command
        is_command = verb in ["help", "status", "quit", "save", "load", "map"]
        
        # If no verb found, treat the whole input as freeform
        if not verb:
            verb = "freeform"
            target = cleaned
        
        return {
            "verb": verb,
            "target": target,
            "original": original,
            "is_command": is_command,
        }
    
    @classmethod
    def get_direction(cls, target: Optional[str]) -> Optional[str]:
        """
        Extract a direction from a target string.
        
        Args:
            target: The target string to parse
            
        Returns:
            Normalized direction or None
        """
        if not target:
            return None
        
        directions = {
            "north": ["north", "n", "up"],
            "south": ["south", "s", "down"],
            "east": ["east", "e", "right"],
            "west": ["west", "w", "left"],
            "northeast": ["northeast", "ne"],
            "northwest": ["northwest", "nw"],
            "southeast": ["southeast", "se"],
            "southwest": ["southwest", "sw"],
        }
        
        target_lower = target.lower().strip()
        for direction, aliases in directions.items():
            if target_lower in aliases:
                return direction
        
        return target_lower


@dataclass
class Player:
    """
    Represents the player in the game.
    
    Tracks inventory, location, history of choices, and provides
    methods for interacting with the game world.
    
    Attributes:
        name: Player's name
        inventory: List of items the player is carrying
        current_location: Current location name
        visited_locations: Set of all locations visited
        choice_history: List of choices made (as node IDs)
        action_history: List of actions taken (as command dicts)
        state_history: List of PlayerState snapshots
        flags: Dict of boolean flags for game state
        variables: Dict of variable values for game state
    """
    
    name: str = "Traveler"
    inventory: list[str] = field(default_factory=list)
    current_location: str = "the beginning"
    visited_locations: set[str] = field(default_factory=set)
    choice_history: list[str] = field(default_factory=list)
    action_history: list[dict] = field(default_factory=list)
    state_history: list[PlayerState] = field(default_factory=list)
    flags: dict[str, bool] = field(default_factory=dict)
    variables: dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize player state after dataclass init.
        
        Adds the current location to visited locations and saves
        the initial state to history.
        """
        self.visited_locations.add(self.current_location)
        self._save_state()
    
    def _save_state(self) -> None:
        """Save current state to history.
        
        Creates a PlayerState snapshot of the current player state
        and appends it to the state history.
        """
        state = PlayerState(
            location=self.current_location,
            inventory=self.inventory.copy(),
            visited_locations=self.visited_locations.copy(),
            choice_count=len(self.choice_history),
        )
        self.state_history.append(state)
    
    def add_item(self, item: str) -> bool:
        """
        Add an item to the player's inventory.
        
        Args:
            item: Name of the item to add
            
        Returns:
            True if item was added (wasn't already present)
        """
        item_lower = item.lower()
        if item_lower not in [i.lower() for i in self.inventory]:
            self.inventory.append(item)
            return True
        return False
    
    def remove_item(self, item: str) -> bool:
        """
        Remove an item from the player's inventory.
        
        Args:
            item: Name of the item to remove
            
        Returns:
            True if item was removed, False if not found
        """
        item_lower = item.lower()
        for i, inv_item in enumerate(self.inventory):
            if inv_item.lower() == item_lower:
                self.inventory.pop(i)
                return True
        return False
    
    def has_item(self, item: str) -> bool:
        """
        Check if player has an item.
        
        Args:
            item: Name of the item to check
            
        Returns:
            True if player has the item
        """
        item_lower = item.lower()
        return any(i.lower() == item_lower for i in self.inventory)
    
    def move_to(self, location: str) -> None:
        """
        Move the player to a new location.
        
        Args:
            location: Name of the new location
        """
        self.current_location = location
        self.visited_locations.add(location)
        self._save_state()
    
    def record_choice(self, node_id: str, command: dict) -> None:
        """
        Record a choice made by the player.
        
        Args:
            node_id: ID of the story node for this choice
            command: The parsed command dictionary
        """
        self.choice_history.append(node_id)
        self.action_history.append(command)
        self._save_state()
    
    def set_flag(self, flag: str, value: bool = True) -> None:
        """
        Set a boolean flag.
        
        Args:
            flag: Name of the flag
            value: Value to set (default True)
        """
        self.flags[flag.lower()] = value
    
    def get_flag(self, flag: str) -> bool:
        """
        Get a boolean flag value.
        
        Args:
            flag: Name of the flag
            
        Returns:
            Flag value (False if not set)
        """
        return self.flags.get(flag.lower(), False)
    
    def set_variable(self, name: str, value: any) -> None:
        """
        Set a variable value.
        
        Args:
            name: Variable name
            value: Value to set
        """
        self.variables[name.lower()] = value
    
    def get_variable(self, name: str, default: any = None) -> any:
        """
        Get a variable value.
        
        Args:
            name: Variable name
            default: Default value if not set
            
        Returns:
            Variable value or default
        """
        return self.variables.get(name.lower(), default)
    
    def get_status(self) -> str:
        """
        Get a formatted status string.
        
        Returns:
            Formatted string with player status
        """
        lines = [
            f"╔{'═' * 40}╗",
            f"║ Player: {self.name:<30}║",
            f"║ Location: {self.current_location:<28}║",
            f"╠{'═' * 40}╣",
            f"║ Inventory:{'':29}║",
        ]
        
        if self.inventory:
            for item in self.inventory:
                lines.append(f"║   • {item:<34}║")
        else:
            lines.append(f"║   (empty){'':29}║")
        
        lines.extend([
            f"╠{'═' * 40}╣",
            f"║ Locations visited: {len(self.visited_locations):<19}║",
            f"║ Choices made: {len(self.choice_history):<24}║",
            f"╚{'═' * 40}╝",
        ])
        
        return "\n".join(lines)
    
    def has_visited(self, location: str) -> bool:
        """
        Check if player has visited a location.
        
        Args:
            location: Location name to check
            
        Returns:
            True if location was visited
        """
        return location.lower() in [loc.lower() for loc in self.visited_locations]
    
    def get_action_pattern(self) -> list[str]:
        """
        Get the pattern of actions taken.
        
        Returns:
            List of verb actions taken
        """
        return [action.get("verb", "unknown") for action in self.action_history]
    
    def detect_action_loop(self, window_size: int = 5) -> Optional[list[str]]:
        """
        Detect if the player is stuck in an action loop.
        
        Checks if the last 'window_size' actions repeat a pattern.
        
        Args:
            window_size: Number of recent actions to check
            
        Returns:
            The repeating pattern if found, None otherwise
        """
        pattern = self.get_action_pattern()
        if len(pattern) < window_size * 2:
            return None
        
        recent = pattern[-window_size:]
        previous = pattern[-window_size * 2:-window_size]
        
        if recent == previous:
            return recent
        
        return None
    
    def to_dict(self) -> dict:
        """Convert player to dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the player.
        """
        return {
            "name": self.name,
            "inventory": self.inventory.copy(),
            "current_location": self.current_location,
            "visited_locations": list(self.visited_locations),
            "choice_history": self.choice_history.copy(),
            "action_history": self.action_history.copy(),
            "state_history": [s.to_dict() for s in self.state_history],
            "flags": self.flags.copy(),
            "variables": self.variables.copy(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Create Player from dictionary.
        
        Args:
            data: Dictionary containing player data.
            
        Returns:
            Player: A new Player instance with restored state.
        """
        player = cls(
            name=data.get("name", "Traveler"),
            inventory=data.get("inventory", []),
            current_location=data.get("current_location", "the beginning"),
            visited_locations=set(data.get("visited_locations", [])),
            choice_history=data.get("choice_history", []),
            action_history=data.get("action_history", []),
            flags=data.get("flags", {}),
            variables=data.get("variables", {}),
        )
        # Restore state history
        player.state_history = [
            PlayerState.from_dict(s) for s in data.get("state_history", [])
        ]
        return player
    
    def __str__(self) -> str:
        """Return string representation.
        
        Returns:
            str: Human-readable string describing the player.
        """
        return f"Player({self.name}, location={self.current_location}, items={len(self.inventory)})"
