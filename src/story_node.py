"""
Story Node Module - Defines the StoryNode class for narrative structures.

This module contains the StoryNode class which represents a single scene
or narrative state in the Infinite Story Loop game. Each node contains
story text, choices, consequences, and links to other nodes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum, auto
import uuid
import copy


class NodeType(Enum):
    """Enumeration of story node types."""
    
    NARRATIVE = auto()      # Standard story text
    CHOICE = auto()         # Player decision point
    CONSEQUENCE = auto()    # Result of player action
    PARADOX = auto()        # Generated paradox resolution
    LOOP_BREAK = auto()     # Node created to break a loop
    SURREAL = auto()        # Randomly injected surreal event


@dataclass
class Choice:
    """
    Represents a single choice available to the player at a story node.
    
    Attributes:
        text: The displayed choice text
        target_node_id: ID of the node this choice leads to (if known)
        action: The action keyword/phrase for this choice
        condition: Optional callable that returns True if choice is available
        consequences: Dict of state changes when this choice is made
    """
    
    text: str
    target_node_id: Optional[str] = None
    action: str = ""
    condition: Optional[Callable[['Player'], bool]] = None
    consequences: dict = field(default_factory=dict)
    
    def is_available(self, player: 'Player') -> bool:
        """Check if this choice is available to the player.

        Args:
            player: The player to check availability for.

        Returns:
            True if the choice is available, False otherwise.
        """
        if self.condition is None:
            return True
        return self.condition(player)
    
    def to_dict(self) -> dict:
        """Convert choice to dictionary for serialization.

        Returns:
            Dictionary representation of the choice.
        """
        return {
            "text": self.text,
            "target_node_id": self.target_node_id,
            "action": self.action,
            "consequences": self.consequences,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Choice':
        """Create a Choice from a dictionary.

        Args:
            data: Dictionary containing choice data.

        Returns:
            A new Choice instance.
        """
        return cls(
            text=data.get("text", ""),
            target_node_id=data.get("target_node_id"),
            action=data.get("action", ""),
            consequences=data.get("consequences", {}),
        )


@dataclass
class StoryNode:
    """
    Represents a single scene or narrative state in the story.
    
    A StoryNode is the fundamental building block of the narrative structure.
    It contains the story text displayed to the player, available choices,
    references to previous nodes (for paradox detection), and metadata
    about how/when the node was created or modified.
    
    Attributes:
        id: Unique identifier for this node
        text: The narrative text displayed to the player
        node_type: Type of node (narrative, choice, paradox, etc.)
        choices: List of available choices at this node
        previous_node_ids: IDs of nodes that can lead to this one
        tags: Set of descriptive tags for categorization
        metadata: Additional data about the node
        is_rewritten: Whether this node has been rewritten due to paradox
        original_text: Original text before any rewrites
        rewrite_count: Number of times this node has been rewritten
        location: The location/scene name for this node
        required_items: Items needed to access this node
        grants_items: Items given to player at this node
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    node_type: NodeType = NodeType.NARRATIVE
    choices: list[Choice] = field(default_factory=list)
    previous_node_ids: list[str] = field(default_factory=list)
    tags: set[str] = field(default_factory=set)
    metadata: dict = field(default_factory=dict)
    is_rewritten: bool = False
    original_text: Optional[str] = None
    rewrite_count: int = 0
    location: str = "unknown"
    required_items: list[str] = field(default_factory=list)
    grants_items: list[str] = field(default_factory=list)
    
    def add_choice(self, choice: Choice) -> None:
        """
        Add a choice to this node.
        
        Args:
            choice: The Choice object to add
        """
        self.choices.append(choice)
    
    def remove_choice(self, action: str) -> bool:
        """
        Remove a choice by its action keyword.
        
        Args:
            action: The action keyword of the choice to remove
            
        Returns:
            True if a choice was removed, False otherwise
        """
        for i, choice in enumerate(self.choices):
            if choice.action.lower() == action.lower():
                self.choices.pop(i)
                return True
        return False
    
    def get_choice_by_action(self, action: str) -> Optional[Choice]:
        """
        Find a choice by its action keyword.
        
        Args:
            action: The action keyword to search for
            
        Returns:
            The matching Choice or None
        """
        action_lower = action.lower()
        for choice in self.choices:
            if choice.action.lower() == action_lower:
                return choice
        return None
    
    def get_available_choices(self, player: 'Player') -> list[Choice]:
        """
        Get all choices available to the given player.
        
        Args:
            player: The player to check availability for
            
        Returns:
            List of available Choice objects
        """
        return [c for c in self.choices if c.is_available(player)]
    
    def rewrite(self, new_text: str, reason: str = "paradox") -> None:
        """
        Rewrite this node's text to resolve a paradox or loop.
        
        This method preserves the original text and tracks rewrite history.
        The metadata is updated with rewrite information.
        
        Args:
            new_text: The new narrative text
            reason: The reason for the rewrite
        """
        if not self.is_rewritten:
            self.original_text = self.text
        
        self.text = new_text
        self.is_rewritten = True
        self.rewrite_count += 1
        
        # Track rewrite history in metadata
        if "rewrite_history" not in self.metadata:
            self.metadata["rewrite_history"] = []
        
        self.metadata["rewrite_history"].append({
            "reason": reason,
            "rewrite_number": self.rewrite_count,
        })
    
    def clone(self) -> 'StoryNode':
        """
        Create a deep copy of this node with a new ID.
        
        Returns:
            A new StoryNode with copied data and a fresh ID
        """
        new_node = copy.deepcopy(self)
        new_node.id = str(uuid.uuid4())
        new_node.previous_node_ids = [self.id]
        return new_node
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to this node.

        Args:
            tag: The tag to add (will be lowercased).
        """
        self.tags.add(tag.lower())
    
    def has_tag(self, tag: str) -> bool:
        """Check if this node has a specific tag.

        Args:
            tag: The tag to check for.

        Returns:
            True if the node has the tag, False otherwise.
        """
        return tag.lower() in self.tags
    
    def to_dict(self) -> dict:
        """
        Convert this node to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the node
        """
        return {
            "id": self.id,
            "text": self.text,
            "node_type": self.node_type.name,
            "choices": [c.to_dict() for c in self.choices],
            "previous_node_ids": self.previous_node_ids,
            "tags": list(self.tags),
            "metadata": self.metadata,
            "is_rewritten": self.is_rewritten,
            "original_text": self.original_text,
            "rewrite_count": self.rewrite_count,
            "location": self.location,
            "required_items": self.required_items,
            "grants_items": self.grants_items,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StoryNode':
        """
        Create a StoryNode from a dictionary.
        
        Args:
            data: Dictionary containing node data
            
        Returns:
            A new StoryNode instance
        """
        node = cls(
            id=data.get("id", str(uuid.uuid4())),
            text=data.get("text", ""),
            node_type=NodeType[data.get("node_type", "NARRATIVE")],
            choices=[Choice.from_dict(c) for c in data.get("choices", [])],
            previous_node_ids=data.get("previous_node_ids", []),
            tags=set(data.get("tags", [])),
            metadata=data.get("metadata", {}),
            is_rewritten=data.get("is_rewritten", False),
            original_text=data.get("original_text"),
            rewrite_count=data.get("rewrite_count", 0),
            location=data.get("location", "unknown"),
            required_items=data.get("required_items", []),
            grants_items=data.get("grants_items", []),
        )
        return node
    
    def __str__(self) -> str:
        """Return a string representation of the node.

        Returns:
            A human-readable string describing the node.
        """
        return f"StoryNode({self.id[:8]}..., location={self.location}, type={self.node_type.name})"
    
    def __repr__(self) -> str:
        """Return a detailed string representation.

        Returns:
            A detailed string suitable for debugging.
        """
        return (
            f"StoryNode(id={self.id!r}, location={self.location!r}, "
            f"type={self.node_type.name}, choices={len(self.choices)}, "
            f"rewritten={self.is_rewritten})"
        )


class StoryGraph:
    """
    Manages the collection of story nodes and their connections.
    
    The StoryGraph maintains all nodes in the story and provides
    methods for traversing, searching, and manipulating the narrative
    structure. It also supports detecting cycles and finding paths.
    
    Attributes:
        nodes: Dictionary mapping node IDs to StoryNode objects
        root_id: ID of the starting node
    """
    
    def __init__(self):
        """Initialize an empty story graph.

        Creates a new StoryGraph with no nodes and no root.
        """
        self.nodes: dict[str, StoryNode] = {}
        self.root_id: Optional[str] = None
    
    def add_node(self, node: StoryNode) -> None:
        """
        Add a node to the graph.
        
        Args:
            node: The StoryNode to add
        """
        self.nodes[node.id] = node
        if self.root_id is None:
            self.root_id = node.id
    
    def get_node(self, node_id: str) -> Optional[StoryNode]:
        """
        Get a node by its ID.
        
        Args:
            node_id: The ID of the node to retrieve
            
        Returns:
            The StoryNode or None if not found
        """
        return self.nodes.get(node_id)
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the graph.
        
        Args:
            node_id: The ID of the node to remove
            
        Returns:
            True if the node was removed, False otherwise
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
            return True
        return False
    
    def get_nodes_by_location(self, location: str) -> list[StoryNode]:
        """
        Get all nodes at a specific location.
        
        Args:
            location: The location name to search for
            
        Returns:
            List of nodes at that location
        """
        return [n for n in self.nodes.values() if n.location == location]
    
    def get_nodes_by_tag(self, tag: str) -> list[StoryNode]:
        """
        Get all nodes with a specific tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List of nodes with that tag
        """
        return [n for n in self.nodes.values() if n.has_tag(tag)]
    
    def find_path(self, start_id: str, end_id: str) -> Optional[list[str]]:
        """
        Find a path between two nodes using BFS.
        
        Args:
            start_id: ID of the starting node
            end_id: ID of the target node
            
        Returns:
            List of node IDs representing the path, or None if no path exists
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return None
        
        if start_id == end_id:
            return [start_id]
        
        visited = {start_id}
        queue = [(start_id, [start_id])]
        
        while queue:
            current_id, path = queue.pop(0)
            current_node = self.nodes[current_id]
            
            for choice in current_node.choices:
                next_id = choice.target_node_id
                if next_id and next_id not in visited:
                    if next_id == end_id:
                        return path + [next_id]
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))
        
        return None
    
    def detect_cycles(self) -> list[list[str]]:
        """
        Detect all cycles in the story graph.
        
        Uses DFS to find cycles. Each cycle is represented as a list
        of node IDs forming the cycle.
        
        Returns:
            List of cycles, where each cycle is a list of node IDs
        """
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str, path: list[str]) -> None:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            node = self.nodes.get(node_id)
            if node:
                for choice in node.choices:
                    next_id = choice.target_node_id
                    if next_id:
                        if next_id not in visited:
                            dfs(next_id, path.copy())
                        elif next_id in rec_stack:
                            # Found a cycle
                            cycle_start = path.index(next_id)
                            cycle = path[cycle_start:] + [next_id]
                            cycles.append(cycle)
            
            rec_stack.discard(node_id)
        
        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id, [])
        
        return cycles
    
    def to_dict(self) -> dict:
        """Convert the graph to a dictionary for serialization.

        Returns:
            Dictionary representation of the graph.
        """
        return {
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "root_id": self.root_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StoryGraph':
        """Create a StoryGraph from a dictionary.

        Args:
            data: Dictionary containing graph data.

        Returns:
            A new StoryGraph instance.
        """
        graph = cls()
        for node_data in data.get("nodes", {}).values():
            graph.add_node(StoryNode.from_dict(node_data))
        graph.root_id = data.get("root_id")
        return graph
    
    def __len__(self) -> int:
        """Return the number of nodes in the graph.

        Returns:
            The number of nodes in the graph.
        """
        return len(self.nodes)
    
    def __contains__(self, node_id: str) -> bool:
        """Check if a node ID is in the graph.

        Args:
            node_id: The ID of the node to check.

        Returns:
            True if the node is in the graph, False otherwise.
        """
        return node_id in self.nodes
