"""
Story Loop Module - Main story engine with paradox detection and resolution.

This module contains the InfiniteStoryLoop class which is the core engine
of the game. It manages the current story path, complete history, detects
loops and contradictions, and dynamically rewrites story nodes to resolve
paradoxes while maintaining narrative continuity.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum, auto

from .story_node import StoryNode, StoryGraph, Choice, NodeType
from .player import Player, CommandParser
from .utils import (
    HistoryTracker,
    GameLogger,
    get_random_surreal_event,
    format_story_text,
)


class ParadoxType(Enum):
    """Types of paradoxes that can be detected."""
    
    TEMPORAL_LOOP = auto()       # Player stuck in a repeating sequence
    CONTRADICTION = auto()        # Actions that logically contradict
    IMPOSSIBLE_STATE = auto()     # State that shouldn't be reachable
    NARRATIVE_BREAK = auto()      # Story continuity broken
    CAUSAL_PARADOX = auto()       # Cause and effect reversed


@dataclass
class Paradox:
    """
    Represents a detected paradox in the story.
    
    Attributes:
        paradox_type: The type of paradox
        description: Human-readable description
        affected_nodes: IDs of nodes involved in the paradox
        trigger_action: The action that triggered the paradox
        severity: How severe the paradox is (1-10)
        metadata: Additional paradox information
    """
    
    paradox_type: ParadoxType
    description: str
    affected_nodes: list[str] = field(default_factory=list)
    trigger_action: str = ""
    severity: int = 5
    metadata: dict = field(default_factory=dict)


class StoryGenerator:
    """
    Generates dynamic story content based on context.
    
    This class contains templates and methods for generating
    new story text, including paradox resolutions and surreal events.
    """
    
    # Story templates for different situations
    TEMPLATES = {
        "intro": [
            "You find yourself in {location}. The air feels thick with possibility, "
            "as if reality itself is waiting to see what you'll do next.",
            "The world around you shifts into focus. You are standing in {location}, "
            "though how you got here remains a mystery wrapped in fog.",
            "{location} materializes around you. Time seems uncertain here, "
            "as if past and future are merely suggestions.",
        ],
        "paradox_resolution": [
            "Reality shudders and rewrites itself. What once was {old_state} "
            "has always been {new_state}. You remember it both ways simultaneously.",
            "The universe course-corrects. {contradiction} never happened, or rather, "
            "it happened differently. Your memories blur and reform.",
            "A ripple passes through existence. The paradox resolves itself by "
            "declaring that {resolution}. This was always true.",
        ],
        "loop_break": [
            "You feel a strange sensation of déjà vu, but... different. "
            "The loop cracks, and new possibilities emerge.",
            "Time stutters. You've been here before, but now the path diverges. "
            "Something has changed in the fabric of this story.",
            "The narrative recognizes the pattern and rebels. "
            "A new thread weaves itself into existence, breaking the cycle.",
        ],
        "surreal_transition": [
            "The boundaries between scenes dissolve momentarily. "
            "You catch glimpses of paths not taken.",
            "Reality hiccups. For an instant, you exist everywhere and nowhere.",
            "The story pauses to reconsider its choices. You wait in the space between words.",
        ],
        "location_descriptions": {
            "the beginning": "an endless white expanse where stories are born",
            "the crossroads": "a place where infinite paths converge and diverge",
            "the library": "towering shelves of unwritten books stretch into infinity",
            "the mirror hall": "reflections show versions of yourself that made different choices",
            "the garden": "flowers bloom in colors that don't exist, narrating forgotten tales",
            "the void": "pure nothingness that somehow contains everything",
            "the clock tower": "gears turn backwards and forwards, keeping time with no time",
            "the market": "traders barter in memories and sell bottled possibilities",
        },
    }
    
    # Character templates
    CHARACTERS = {
        "the narrator": {
            "description": "A voice without a body, speaking from everywhere and nowhere",
            "personality": "cryptic, amused, occasionally breaking the fourth wall",
        },
        "the echo": {
            "description": "A shadow that mirrors your past actions",
            "personality": "silent, reflective, sometimes contradictory",
        },
        "the keeper": {
            "description": "An ancient figure who maintains the story's continuity",
            "personality": "weary, helpful, knows more than they say",
        },
        "the glitch": {
            "description": "A character that shouldn't exist, born from paradoxes",
            "personality": "erratic, insightful, speaks in corrupted text",
        },
    }
    
    @classmethod
    def generate_intro(cls, location: str) -> str:
        """Generate an introduction for a location."""
        template = random.choice(cls.TEMPLATES["intro"])
        location_desc = cls.TEMPLATES["location_descriptions"].get(
            location, f"a place called {location}"
        )
        return template.format(location=location_desc)
    
    @classmethod
    def generate_paradox_resolution(
        cls,
        paradox: Paradox,
        player: Player
    ) -> str:
        """
        Generate text to resolve a paradox.
        
        Args:
            paradox: The paradox to resolve
            player: Current player state
            
        Returns:
            Generated resolution text
        """
        template = random.choice(cls.TEMPLATES["paradox_resolution"])
        
        # Build resolution context
        old_state = paradox.metadata.get("old_state", "one reality")
        new_state = paradox.metadata.get("new_state", "another")
        contradiction = paradox.trigger_action
        resolution = f"both states exist in superposition until observed"
        
        text = template.format(
            old_state=old_state,
            new_state=new_state,
            contradiction=contradiction,
            resolution=resolution,
        )
        
        # Add surreal event sometimes
        if random.random() < 0.4:
            text += f"\n\n{get_random_surreal_event()}"
        
        return text
    
    @classmethod
    def generate_loop_break(cls) -> str:
        """Generate text for breaking a narrative loop."""
        text = random.choice(cls.TEMPLATES["loop_break"])
        if random.random() < 0.3:
            text += f"\n\n{get_random_surreal_event()}"
        return text
    
    @classmethod
    def generate_choices(cls, location: str, player: Player) -> list[Choice]:
        """
        Generate dynamic choices based on current state.
        
        Args:
            location: Current location
            player: Current player state
            
        Returns:
            List of generated choices
        """
        choices = []
        
        # Basic movement choices
        directions = ["north", "south", "east", "west"]
        available_dirs = random.sample(directions, random.randint(2, 4))
        
        for direction in available_dirs:
            choices.append(Choice(
                text=f"Go {direction}",
                action=f"go {direction}",
            ))
        
        # Location-specific choices
        if "library" in location:
            choices.append(Choice(
                text="Read a book",
                action="read book",
            ))
        elif "market" in location:
            choices.append(Choice(
                text="Browse the wares",
                action="browse",
            ))
        elif "mirror" in location:
            choices.append(Choice(
                text="Touch the mirror",
                action="touch mirror",
            ))
        
        # Add examine option
        choices.append(Choice(
            text="Look around",
            action="look",
        ))
        
        return choices


class InfiniteStoryLoop:
    """
    Main story engine that manages the narrative and detects paradoxes.
    
    The InfiniteStoryLoop maintains the current story state, tracks all
    player actions, detects when loops or contradictions occur, and
    dynamically rewrites the story to resolve these paradoxes while
    keeping the narrative engaging and immersive.
    
    Attributes:
        story_graph: The complete story structure
        current_node: Currently active story node
        player: The player state
        history: History tracker for paradox detection
        logger: Game event logger
        paradox_count: Number of paradoxes detected
        rewrite_count: Number of story rewrites performed
    """
    
    def __init__(
        self,
        player: Optional[Player] = None,
        logger: Optional[GameLogger] = None
    ):
        """
        Initialize the Infinite Story Loop engine.
        
        Args:
            player: Player instance (created if None)
            logger: Logger instance (created if None)
        """
        self.story_graph = StoryGraph()
        self.current_node: Optional[StoryNode] = None
        self.player = player or Player()
        self.history = HistoryTracker()
        self.logger = logger or GameLogger()
        self.paradox_count = 0
        self.rewrite_count = 0
        self._initialize_story()
    
    def _initialize_story(self) -> None:
        """Set up the initial story state."""
        # Create the starting node
        intro_text = StoryGenerator.generate_intro("the beginning")
        
        start_node = StoryNode(
            text=intro_text,
            node_type=NodeType.NARRATIVE,
            location="the beginning",
        )
        
        # Add initial choices
        start_node.choices = [
            Choice(text="Walk towards the light", action="go north"),
            Choice(text="Follow the shadows", action="go south"),
            Choice(text="Listen to the whispers", action="listen"),
            Choice(text="Question your existence", action="think"),
        ]
        
        self.story_graph.add_node(start_node)
        self.current_node = start_node
        
        self.logger.story(f"Story initialized at: {start_node.location}")
    
    def process_input(self, raw_input: str) -> dict:
        """
        Process player input and advance the story.
        
        This is the main entry point for player interaction. It parses
        the input, checks for paradoxes, generates new content, and
        returns the result to display.
        
        Args:
            raw_input: Raw input string from the player
            
        Returns:
            Dict containing response type, text, choices, and metadata
        """
        # Parse the input
        command = CommandParser.parse(raw_input)
        
        # Handle system commands
        if command["is_command"]:
            return self._handle_system_command(command)
        
        # Check for paradoxes before processing the action
        paradox = self._detect_paradox(command)
        
        if paradox:
            return self._handle_paradox(paradox, command)
        
        # Process the action and advance the story
        return self._advance_story(command)
    
    def _handle_system_command(self, command: dict) -> dict:
        """
        Handle system commands (help, status, quit, etc.).
        
        Args:
            command: Parsed command dictionary
            
        Returns:
            Response dictionary
        """
        verb = command["verb"]
        
        if verb == "help":
            help_text = self._get_help_text()
            return {
                "type": "system",
                "text": help_text,
                "choices": [],
            }
        
        elif verb == "status":
            status_text = self.player.get_status()
            return {
                "type": "system",
                "text": status_text,
                "choices": [],
            }
        
        elif verb == "quit":
            return {
                "type": "quit",
                "text": "The story folds itself away, waiting for another time...",
                "choices": [],
            }
        
        elif verb == "map":
            map_text = self._get_story_map()
            return {
                "type": "system",
                "text": map_text,
                "choices": [],
            }
        
        elif verb == "save":
            return {
                "type": "save",
                "text": "Saving story state...",
                "choices": [],
            }
        
        elif verb == "load":
            return {
                "type": "load",
                "text": "Loading story state...",
                "choices": [],
            }
        
        return {
            "type": "error",
            "text": f"Unknown command: {verb}",
            "choices": [],
        }
    
    def _detect_paradox(self, command: dict) -> Optional[Paradox]:
        """
        Detect if the current action creates a paradox.
        
        Checks for:
        - Temporal loops (repeating action sequences)
        - Contradictions (conflicting actions)
        - Impossible states (states that shouldn't be reachable)
        
        Args:
            command: The parsed command to check
            
        Returns:
            Paradox object if detected, None otherwise
        """
        # Check for action loops
        action_loop = self.player.detect_action_loop()
        if action_loop:
            self.logger.paradox(f"Action loop detected: {action_loop}")
            return Paradox(
                paradox_type=ParadoxType.TEMPORAL_LOOP,
                description=f"You find yourself repeating the same actions: {', '.join(action_loop)}",
                trigger_action=command.get("original", ""),
                severity=6,
                metadata={"loop_pattern": action_loop},
            )
        
        # Check for node visit loops
        node_loop = self.history.detect_node_loop()
        if node_loop:
            self.logger.paradox(f"Node loop detected: {node_loop}")
            return Paradox(
                paradox_type=ParadoxType.TEMPORAL_LOOP,
                description="The story seems to be repeating itself...",
                affected_nodes=node_loop,
                trigger_action=command.get("original", ""),
                severity=7,
            )
        
        # Check for contradictions
        action = f"{command.get('verb', '')} {command.get('target', '') or ''}".strip()
        contradiction = self.history.detect_contradiction(
            action,
            command.get("target")
        )
        
        if contradiction:
            self.logger.paradox(f"Contradiction detected: {contradiction}")
            return Paradox(
                paradox_type=ParadoxType.CONTRADICTION,
                description=f"Your action contradicts a previous choice...",
                trigger_action=command.get("original", ""),
                severity=8,
                metadata=contradiction,
            )
        
        # Check for impossible states (e.g., using item you don't have)
        if command.get("verb") == "use":
            target = command.get("target")
            if target and not self.player.has_item(target):
                return Paradox(
                    paradox_type=ParadoxType.IMPOSSIBLE_STATE,
                    description=f"You try to use {target}, but you don't have it... or do you?",
                    trigger_action=command.get("original", ""),
                    severity=5,
                    metadata={"missing_item": target},
                )
        
        return None
    
    def _handle_paradox(self, paradox: Paradox, command: dict) -> dict:
        """
        Handle a detected paradox by rewriting the story.
        
        This method generates new story content to resolve the paradox
        while maintaining narrative continuity and immersion.
        
        Args:
            paradox: The detected paradox
            command: The triggering command
            
        Returns:
            Response dictionary with paradox resolution
        """
        self.paradox_count += 1
        self.logger.paradox(
            f"Handling paradox #{self.paradox_count}: {paradox.paradox_type.name}"
        )
        
        # Generate resolution text
        resolution_text = StoryGenerator.generate_paradox_resolution(
            paradox, self.player
        )
        
        # Rewrite affected nodes if necessary
        if paradox.affected_nodes:
            for node_id in paradox.affected_nodes:
                node = self.story_graph.get_node(node_id)
                if node:
                    self._rewrite_node(node, paradox)
        
        # Create a new node for the paradox resolution
        resolution_node = StoryNode(
            text=resolution_text,
            node_type=NodeType.PARADOX,
            location=self.player.current_location,
            previous_node_ids=[self.current_node.id] if self.current_node else [],
        )
        
        # Generate new choices after paradox
        resolution_node.choices = self._generate_post_paradox_choices(paradox)
        
        self.story_graph.add_node(resolution_node)
        self.current_node = resolution_node
        
        # Record in history
        self.history.add_entry(
            resolution_node.id,
            f"paradox_resolution:{paradox.paradox_type.name}",
            self._get_state_snapshot(),
            {"paradox": paradox.description},
        )
        
        return {
            "type": "paradox",
            "text": format_story_text(resolution_text),
            "choices": [c.text for c in resolution_node.choices],
            "paradox_type": paradox.paradox_type.name,
            "severity": paradox.severity,
        }
    
    def _rewrite_node(self, node: StoryNode, paradox: Paradox) -> None:
        """
        Rewrite a story node to resolve a paradox.
        
        Args:
            node: The node to rewrite
            paradox: The paradox being resolved
        """
        self.rewrite_count += 1
        
        # Generate new text based on paradox type
        if paradox.paradox_type == ParadoxType.TEMPORAL_LOOP:
            new_text = (
                f"{node.text}\n\n"
                f"[The narrative shifts subtly. This moment is different now, "
                f"though you can't quite say how.]"
            )
        elif paradox.paradox_type == ParadoxType.CONTRADICTION:
            new_text = (
                f"{node.text}\n\n"
                f"[Reality rewrites itself. The contradiction resolves into "
                f"a strange new truth that somehow makes sense.]"
            )
        else:
            new_text = f"{node.text}\n\n[The story adjusts itself...]"
        
        node.rewrite(new_text, reason=paradox.paradox_type.name)
        self.logger.story(f"Rewrote node {node.id[:8]} due to {paradox.paradox_type.name}")
    
    def _generate_post_paradox_choices(self, paradox: Paradox) -> list[Choice]:
        """
        Generate choices after a paradox resolution.
        
        Args:
            paradox: The resolved paradox
            
        Returns:
            List of new choices
        """
        choices = [
            Choice(
                text="Accept the new reality",
                action="accept",
            ),
            Choice(
                text="Question what just happened",
                action="question",
            ),
        ]
        
        # Add paradox-specific choices
        if paradox.paradox_type == ParadoxType.TEMPORAL_LOOP:
            choices.append(Choice(
                text="Try to break the cycle",
                action="break cycle",
            ))
        elif paradox.paradox_type == ParadoxType.CONTRADICTION:
            choices.append(Choice(
                text="Embrace the contradiction",
                action="embrace",
            ))
        
        # Add standard movement choice
        choices.append(Choice(
            text="Move on",
            action="go forward",
        ))
        
        return choices
    
    def _advance_story(self, command: dict) -> dict:
        """
        Advance the story based on player action.
        
        Args:
            command: Parsed command dictionary
            
        Returns:
            Response dictionary with new story content
        """
        # Record the action
        self.player.record_choice(
            self.current_node.id if self.current_node else "unknown",
            command
        )
        
        # Generate the next story beat
        next_node = self._generate_next_node(command)
        
        # Update state
        if self.current_node:
            next_node.previous_node_ids.append(self.current_node.id)
        
        self.story_graph.add_node(next_node)
        self.current_node = next_node
        self.player.move_to(next_node.location)
        
        # Handle item grants
        for item in next_node.grants_items:
            if self.player.add_item(item):
                self.logger.story(f"Player received: {item}")
        
        # Record in history
        self.history.add_entry(
            next_node.id,
            command.get("original", "unknown"),
            self._get_state_snapshot(),
            {"verb": command.get("verb"), "target": command.get("target")},
        )
        
        self.logger.story(f"Advanced to: {next_node.location}")
        
        return {
            "type": "story",
            "text": format_story_text(next_node.text),
            "choices": [c.text for c in next_node.get_available_choices(self.player)],
            "location": next_node.location,
        }
    
    def _generate_next_node(self, command: dict) -> StoryNode:
        """
        Generate the next story node based on the command.
        
        Args:
            command: Parsed command dictionary
            
        Returns:
            New StoryNode for the next scene
        """
        verb = command.get("verb", "")
        target = command.get("target", "")
        
        # Determine new location
        if verb == "go":
            direction = CommandParser.get_direction(target)
            new_location = self._get_location_in_direction(direction)
        else:
            new_location = self.player.current_location
        
        # Generate story text
        text = self._generate_story_text(verb, target, new_location)
        
        # Create the node
        node = StoryNode(
            text=text,
            node_type=NodeType.NARRATIVE,
            location=new_location,
        )
        
        # Generate choices
        node.choices = StoryGenerator.generate_choices(new_location, self.player)
        
        # Potentially grant items
        if random.random() < 0.2:
            items = ["strange key", "glowing orb", "ancient map", "cryptic note"]
            node.grants_items.append(random.choice(items))
            node.text += f"\n\nYou notice something interesting and pick it up."
        
        return node
    
    def _generate_story_text(
        self,
        verb: str,
        target: str,
        location: str
    ) -> str:
        """
        Generate story text for an action.
        
        Args:
            verb: The action verb
            target: The action target
            location: Current/new location
            
        Returns:
            Generated story text
        """
        # Base templates for different actions
        templates = {
            "go": [
                f"You move towards {target or 'the unknown'}. "
                f"The scenery shifts around you as you enter {location}.",
                f"Your footsteps echo as you travel {target or 'onward'}. "
                f"You find yourself in {location}.",
                f"The path leads you {target or 'forward'}. "
                f"{location.title()} materializes around you.",
            ],
            "look": [
                f"You examine your surroundings carefully. "
                f"{StoryGenerator.TEMPLATES['location_descriptions'].get(location, location).capitalize()}.",
                f"You take in the details of {location}. "
                f"Everything seems both familiar and strange.",
            ],
            "take": [
                f"You reach for {target or 'something'}. "
                f"It feels significant in your hands.",
                f"You pick up {target or 'the object'}. "
                f"Reality seems to acknowledge your choice.",
            ],
            "talk": [
                f"You speak to {target or 'the silence'}. "
                f"Words echo in ways they shouldn't.",
                f"You attempt conversation with {target or 'the void'}. "
                f"Something listens.",
            ],
            "think": [
                "You pause to consider your existence. "
                "The story waits patiently for your next move.",
                "Thoughts spiral through your mind. "
                "Are you the author or the authored?",
            ],
            "listen": [
                "You strain to hear the whispers of the narrative. "
                "They speak of paths not yet taken.",
                "The silence hums with unwritten possibilities. "
                "You catch fragments of other stories.",
            ],
        }
        
        # Get appropriate template
        verb_templates = templates.get(verb, templates.get("go"))
        text = random.choice(verb_templates)
        
        # Add occasional surreal elements
        if random.random() < 0.15:
            text += f"\n\n{get_random_surreal_event()}"
        
        return text
    
    def _get_location_in_direction(self, direction: Optional[str]) -> str:
        """
        Get the location name for a given direction.
        
        Args:
            direction: Direction of travel
            
        Returns:
            Location name
        """
        location_map = {
            "north": ["the library", "the clock tower", "the void"],
            "south": ["the garden", "the market", "the beginning"],
            "east": ["the mirror hall", "the crossroads"],
            "west": ["the crossroads", "the garden"],
        }
        
        if direction in location_map:
            return random.choice(location_map[direction])
        
        # Random location for unknown directions
        all_locations = list(StoryGenerator.TEMPLATES["location_descriptions"].keys())
        return random.choice(all_locations)
    
    def _get_state_snapshot(self) -> dict:
        """
        Get a snapshot of the current game state.
        
        Returns:
            Dictionary of current state for hashing
        """
        return {
            "location": self.player.current_location,
            "inventory": sorted(self.player.inventory),
            "node_id": self.current_node.id if self.current_node else None,
            "choice_count": len(self.player.choice_history),
        }
    
    def _get_help_text(self) -> str:
        """Get the help text for the game."""
        return """
╔══════════════════════════════════════════════════════════════════════╗
║                    INFINITE STORY LOOP - HELP                        ║
╠══════════════════════════════════════════════════════════════════════╣
║ MOVEMENT:                                                            ║
║   go [direction]  - Move in a direction (north, south, east, west)   ║
║                                                                      ║
║ ACTIONS:                                                             ║
║   look            - Examine your surroundings                        ║
║   take [item]     - Pick up an item                                  ║
║   drop [item]     - Drop an item from your inventory                 ║
║   use [item]      - Use an item                                      ║
║   talk [target]   - Talk to someone or something                     ║
║                                                                      ║
║ SYSTEM:                                                              ║
║   status / i      - View your status and inventory                   ║
║   help / ?        - Show this help message                           ║
║   map             - View story history and loops                     ║
║   save            - Save your current game                           ║
║   load            - Load a saved game                                ║
║   quit / q        - Exit the game                                    ║
║                                                                      ║
║ TIPS:                                                                ║
║   - Try different actions to explore the narrative                   ║
║   - Contradictory actions may create paradoxes                       ║
║   - The story rewrites itself to maintain continuity                 ║
║   - Embrace the surreal and expect the unexpected                    ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    
    def _get_story_map(self) -> str:
        """Get a visual representation of the story path."""
        lines = [
            "╔══════════════════════════════════════════════════════════════════════╗",
            "║                         STORY MAP                                    ║",
            "╠══════════════════════════════════════════════════════════════════════╣",
        ]
        
        # Show visited locations
        lines.append("║ VISITED LOCATIONS:                                                   ║")
        for loc in self.player.visited_locations:
            indicator = "→" if loc == self.player.current_location else " "
            lines.append(f"║  {indicator} {loc:<64}║")
        
        lines.append("╠══════════════════════════════════════════════════════════════════════╣")
        lines.append("║ STATISTICS:                                                          ║")
        lines.append(f"║   Choices made: {len(self.player.choice_history):<52}║")
        lines.append(f"║   Paradoxes encountered: {self.paradox_count:<43}║")
        lines.append(f"║   Story rewrites: {self.rewrite_count:<50}║")
        lines.append(f"║   Story nodes created: {len(self.story_graph):<45}║")
        lines.append("╚══════════════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def get_current_text(self) -> str:
        """Get the current node's text."""
        if self.current_node:
            return format_story_text(self.current_node.text)
        return "The story has not yet begun..."
    
    def get_current_choices(self) -> list[str]:
        """Get the current available choices."""
        if self.current_node:
            return [c.text for c in self.current_node.get_available_choices(self.player)]
        return []
    
    def to_dict(self) -> dict:
        """Convert game state to dictionary for saving."""
        return {
            "story_graph": self.story_graph.to_dict(),
            "current_node_id": self.current_node.id if self.current_node else None,
            "player": self.player.to_dict(),
            "history": self.history.to_dict(),
            "paradox_count": self.paradox_count,
            "rewrite_count": self.rewrite_count,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InfiniteStoryLoop':
        """Create game instance from dictionary."""
        from .player import Player
        
        game = cls.__new__(cls)
        game.story_graph = StoryGraph.from_dict(data.get("story_graph", {}))
        game.player = Player.from_dict(data.get("player", {}))
        game.history = HistoryTracker.from_dict(data.get("history", {}))
        game.logger = GameLogger()
        game.paradox_count = data.get("paradox_count", 0)
        game.rewrite_count = data.get("rewrite_count", 0)
        
        # Restore current node reference
        current_id = data.get("current_node_id")
        if current_id:
            game.current_node = game.story_graph.get_node(current_id)
        else:
            game.current_node = None
        
        return game
