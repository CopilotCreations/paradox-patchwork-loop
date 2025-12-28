"""
Unit tests for the StoryNode module.

Tests the StoryNode, Choice, and StoryGraph classes including
serialization, node manipulation, and graph operations.
"""

import pytest
import uuid
from src.story_node import StoryNode, Choice, StoryGraph, NodeType


class TestChoice:
    """Tests for the Choice class."""
    
    def test_choice_creation(self):
        """Test creating a basic choice."""
        choice = Choice(text="Go north", action="go north")
        assert choice.text == "Go north"
        assert choice.action == "go north"
        assert choice.target_node_id is None
        assert choice.consequences == {}
    
    def test_choice_with_target(self):
        """Test creating a choice with a target node."""
        target_id = str(uuid.uuid4())
        choice = Choice(
            text="Enter the cave",
            action="enter cave",
            target_node_id=target_id,
        )
        assert choice.target_node_id == target_id
    
    def test_choice_with_consequences(self):
        """Test creating a choice with consequences."""
        choice = Choice(
            text="Take the sword",
            action="take sword",
            consequences={"has_sword": True, "strength": 5},
        )
        assert choice.consequences["has_sword"] is True
        assert choice.consequences["strength"] == 5
    
    def test_choice_is_available_no_condition(self):
        """Test availability check with no condition."""
        choice = Choice(text="Test", action="test")
        # Pass None as player since no condition
        assert choice.is_available(None) is True
    
    def test_choice_is_available_with_condition(self):
        """Test availability check with a condition."""
        from src.player import Player
        
        def has_key(player):
            return player.has_item("key")
        
        choice = Choice(text="Open door", action="open door", condition=has_key)
        
        player_without_key = Player()
        player_with_key = Player()
        player_with_key.add_item("key")
        
        assert choice.is_available(player_without_key) is False
        assert choice.is_available(player_with_key) is True
    
    def test_choice_to_dict(self):
        """Test serializing a choice to dictionary."""
        choice = Choice(
            text="Test choice",
            action="test",
            target_node_id="node123",
            consequences={"flag": True},
        )
        data = choice.to_dict()
        
        assert data["text"] == "Test choice"
        assert data["action"] == "test"
        assert data["target_node_id"] == "node123"
        assert data["consequences"]["flag"] is True
    
    def test_choice_from_dict(self):
        """Test deserializing a choice from dictionary."""
        data = {
            "text": "Walk forward",
            "action": "walk",
            "target_node_id": "abc123",
            "consequences": {"moved": True},
        }
        choice = Choice.from_dict(data)
        
        assert choice.text == "Walk forward"
        assert choice.action == "walk"
        assert choice.target_node_id == "abc123"
        assert choice.consequences["moved"] is True


class TestStoryNode:
    """Tests for the StoryNode class."""
    
    def test_node_creation_defaults(self):
        """Test creating a node with default values."""
        node = StoryNode()
        assert node.id is not None
        assert node.text == ""
        assert node.node_type == NodeType.NARRATIVE
        assert node.choices == []
        assert node.is_rewritten is False
        assert node.rewrite_count == 0
    
    def test_node_creation_with_values(self):
        """Test creating a node with specific values."""
        node = StoryNode(
            text="You are in a dark room.",
            node_type=NodeType.CHOICE,
            location="dark room",
        )
        assert node.text == "You are in a dark room."
        assert node.node_type == NodeType.CHOICE
        assert node.location == "dark room"
    
    def test_add_choice(self):
        """Test adding a choice to a node."""
        node = StoryNode(text="Test node")
        choice = Choice(text="Do something", action="do")
        
        node.add_choice(choice)
        
        assert len(node.choices) == 1
        assert node.choices[0].text == "Do something"
    
    def test_remove_choice(self):
        """Test removing a choice from a node."""
        node = StoryNode()
        node.add_choice(Choice(text="Choice 1", action="c1"))
        node.add_choice(Choice(text="Choice 2", action="c2"))
        
        result = node.remove_choice("c1")
        
        assert result is True
        assert len(node.choices) == 1
        assert node.choices[0].action == "c2"
    
    def test_remove_choice_not_found(self):
        """Test removing a non-existent choice."""
        node = StoryNode()
        node.add_choice(Choice(text="Choice", action="c1"))
        
        result = node.remove_choice("nonexistent")
        
        assert result is False
        assert len(node.choices) == 1
    
    def test_get_choice_by_action(self):
        """Test finding a choice by action."""
        node = StoryNode()
        node.add_choice(Choice(text="Go north", action="go north"))
        node.add_choice(Choice(text="Go south", action="go south"))
        
        choice = node.get_choice_by_action("go north")
        
        assert choice is not None
        assert choice.text == "Go north"
    
    def test_get_choice_by_action_not_found(self):
        """Test finding a non-existent choice."""
        node = StoryNode()
        node.add_choice(Choice(text="Go north", action="go north"))
        
        choice = node.get_choice_by_action("go east")
        
        assert choice is None
    
    def test_get_choice_by_action_case_insensitive(self):
        """Test that action search is case-insensitive."""
        node = StoryNode()
        node.add_choice(Choice(text="Go North", action="Go North"))
        
        choice = node.get_choice_by_action("go north")
        
        assert choice is not None
    
    def test_rewrite_node(self):
        """Test rewriting a node's text."""
        node = StoryNode(text="Original text")
        
        node.rewrite("New text", reason="paradox")
        
        assert node.text == "New text"
        assert node.original_text == "Original text"
        assert node.is_rewritten is True
        assert node.rewrite_count == 1
        assert len(node.metadata["rewrite_history"]) == 1
    
    def test_rewrite_node_multiple_times(self):
        """Test rewriting a node multiple times."""
        node = StoryNode(text="Original")
        
        node.rewrite("First rewrite", reason="loop")
        node.rewrite("Second rewrite", reason="contradiction")
        
        assert node.text == "Second rewrite"
        assert node.original_text == "Original"
        assert node.rewrite_count == 2
        assert len(node.metadata["rewrite_history"]) == 2
    
    def test_clone_node(self):
        """Test cloning a node."""
        original = StoryNode(
            text="Original node",
            location="test location",
        )
        original.add_choice(Choice(text="Choice", action="act"))
        
        clone = original.clone()
        
        assert clone.id != original.id
        assert clone.text == original.text
        assert clone.location == original.location
        assert len(clone.choices) == 1
        assert original.id in clone.previous_node_ids
    
    def test_add_tag(self):
        """Test adding tags to a node."""
        node = StoryNode()
        
        node.add_tag("Important")
        node.add_tag("combat")
        
        assert node.has_tag("important")
        assert node.has_tag("COMBAT")
        assert not node.has_tag("other")
    
    def test_to_dict(self):
        """Test serializing a node to dictionary."""
        node = StoryNode(
            text="Test text",
            node_type=NodeType.PARADOX,
            location="test location",
        )
        node.add_choice(Choice(text="Choice", action="act"))
        node.add_tag("test_tag")
        
        data = node.to_dict()
        
        assert data["text"] == "Test text"
        assert data["node_type"] == "PARADOX"
        assert data["location"] == "test location"
        assert len(data["choices"]) == 1
        assert "test_tag" in data["tags"]
    
    def test_from_dict(self):
        """Test deserializing a node from dictionary."""
        data = {
            "id": "test-id-123",
            "text": "Restored text",
            "node_type": "NARRATIVE",
            "choices": [{"text": "Choice", "action": "act"}],
            "tags": ["important"],
            "location": "restored location",
            "is_rewritten": True,
            "original_text": "Old text",
            "rewrite_count": 2,
        }
        
        node = StoryNode.from_dict(data)
        
        assert node.id == "test-id-123"
        assert node.text == "Restored text"
        assert node.node_type == NodeType.NARRATIVE
        assert len(node.choices) == 1
        assert node.has_tag("important")
        assert node.is_rewritten is True
        assert node.rewrite_count == 2
    
    def test_node_str_representation(self):
        """Test string representation of a node."""
        node = StoryNode(location="test", node_type=NodeType.CHOICE)
        
        str_repr = str(node)
        
        assert "StoryNode" in str_repr
        assert "test" in str_repr
    
    def test_get_available_choices(self):
        """Test getting available choices for a player."""
        from src.player import Player
        
        node = StoryNode()
        node.add_choice(Choice(text="Always available", action="always"))
        node.add_choice(Choice(
            text="Needs key",
            action="locked",
            condition=lambda p: p.has_item("key"),
        ))
        
        player = Player()
        
        available = node.get_available_choices(player)
        
        assert len(available) == 1
        assert available[0].action == "always"
        
        player.add_item("key")
        available = node.get_available_choices(player)
        
        assert len(available) == 2


class TestStoryGraph:
    """Tests for the StoryGraph class."""
    
    def test_graph_creation(self):
        """Test creating an empty graph."""
        graph = StoryGraph()
        assert len(graph) == 0
        assert graph.root_id is None
    
    def test_add_node(self):
        """Test adding a node to the graph."""
        graph = StoryGraph()
        node = StoryNode(text="First node")
        
        graph.add_node(node)
        
        assert len(graph) == 1
        assert graph.root_id == node.id
        assert node.id in graph
    
    def test_add_multiple_nodes(self):
        """Test adding multiple nodes."""
        graph = StoryGraph()
        node1 = StoryNode(text="Node 1")
        node2 = StoryNode(text="Node 2")
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        assert len(graph) == 2
        assert graph.root_id == node1.id  # First node is root
    
    def test_get_node(self):
        """Test retrieving a node by ID."""
        graph = StoryGraph()
        node = StoryNode(text="Test node")
        graph.add_node(node)
        
        retrieved = graph.get_node(node.id)
        
        assert retrieved is not None
        assert retrieved.text == "Test node"
    
    def test_get_node_not_found(self):
        """Test retrieving a non-existent node."""
        graph = StoryGraph()
        
        retrieved = graph.get_node("nonexistent")
        
        assert retrieved is None
    
    def test_remove_node(self):
        """Test removing a node from the graph."""
        graph = StoryGraph()
        node = StoryNode(text="To be removed")
        graph.add_node(node)
        
        result = graph.remove_node(node.id)
        
        assert result is True
        assert len(graph) == 0
        assert node.id not in graph
    
    def test_remove_node_not_found(self):
        """Test removing a non-existent node."""
        graph = StoryGraph()
        
        result = graph.remove_node("nonexistent")
        
        assert result is False
    
    def test_get_nodes_by_location(self):
        """Test finding nodes by location."""
        graph = StoryGraph()
        graph.add_node(StoryNode(text="N1", location="forest"))
        graph.add_node(StoryNode(text="N2", location="cave"))
        graph.add_node(StoryNode(text="N3", location="forest"))
        
        forest_nodes = graph.get_nodes_by_location("forest")
        
        assert len(forest_nodes) == 2
    
    def test_get_nodes_by_tag(self):
        """Test finding nodes by tag."""
        graph = StoryGraph()
        
        node1 = StoryNode(text="N1")
        node1.add_tag("combat")
        
        node2 = StoryNode(text="N2")
        node2.add_tag("puzzle")
        
        node3 = StoryNode(text="N3")
        node3.add_tag("combat")
        
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        
        combat_nodes = graph.get_nodes_by_tag("combat")
        
        assert len(combat_nodes) == 2
    
    def test_find_path_simple(self):
        """Test finding a path between two nodes."""
        graph = StoryGraph()
        
        node1 = StoryNode(text="Start")
        node2 = StoryNode(text="End")
        node1.add_choice(Choice(text="Go", action="go", target_node_id=node2.id))
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        path = graph.find_path(node1.id, node2.id)
        
        assert path is not None
        assert len(path) == 2
        assert path[0] == node1.id
        assert path[1] == node2.id
    
    def test_find_path_same_node(self):
        """Test finding path to same node."""
        graph = StoryGraph()
        node = StoryNode(text="Only node")
        graph.add_node(node)
        
        path = graph.find_path(node.id, node.id)
        
        assert path == [node.id]
    
    def test_find_path_no_connection(self):
        """Test finding path when nodes aren't connected."""
        graph = StoryGraph()
        node1 = StoryNode(text="Node 1")
        node2 = StoryNode(text="Node 2")
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        path = graph.find_path(node1.id, node2.id)
        
        assert path is None
    
    def test_detect_cycles(self):
        """Test detecting cycles in the graph."""
        graph = StoryGraph()
        
        node1 = StoryNode(text="Node 1")
        node2 = StoryNode(text="Node 2")
        node3 = StoryNode(text="Node 3")
        
        # Create a cycle: 1 -> 2 -> 3 -> 1
        node1.add_choice(Choice(text="", action="", target_node_id=node2.id))
        node2.add_choice(Choice(text="", action="", target_node_id=node3.id))
        node3.add_choice(Choice(text="", action="", target_node_id=node1.id))
        
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        
        cycles = graph.detect_cycles()
        
        assert len(cycles) > 0
    
    def test_graph_to_dict(self):
        """Test serializing a graph to dictionary."""
        graph = StoryGraph()
        node1 = StoryNode(text="Node 1")
        node2 = StoryNode(text="Node 2")
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        data = graph.to_dict()
        
        assert "nodes" in data
        assert "root_id" in data
        assert len(data["nodes"]) == 2
    
    def test_graph_from_dict(self):
        """Test deserializing a graph from dictionary."""
        original = StoryGraph()
        original.add_node(StoryNode(text="Node 1", location="loc1"))
        original.add_node(StoryNode(text="Node 2", location="loc2"))
        
        data = original.to_dict()
        restored = StoryGraph.from_dict(data)
        
        assert len(restored) == 2
        assert restored.root_id == original.root_id


class TestNodeType:
    """Tests for the NodeType enum."""
    
    def test_node_types_exist(self):
        """Test that all expected node types exist."""
        assert NodeType.NARRATIVE is not None
        assert NodeType.CHOICE is not None
        assert NodeType.CONSEQUENCE is not None
        assert NodeType.PARADOX is not None
        assert NodeType.LOOP_BREAK is not None
        assert NodeType.SURREAL is not None
    
    def test_node_type_names(self):
        """Test node type name access."""
        assert NodeType.NARRATIVE.name == "NARRATIVE"
        assert NodeType.PARADOX.name == "PARADOX"
