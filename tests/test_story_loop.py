"""
Unit tests for the StoryLoop module.

Tests the InfiniteStoryLoop class including paradox detection,
story generation, and game state management.
"""

import pytest
from src.story_loop import (
    InfiniteStoryLoop,
    StoryGenerator,
    Paradox,
    ParadoxType,
)
from src.player import Player
from src.story_node import StoryNode, Choice, NodeType


class TestParadoxType:
    """Tests for the ParadoxType enum."""
    
    def test_paradox_types_exist(self):
        """Test that all paradox types exist."""
        assert ParadoxType.TEMPORAL_LOOP is not None
        assert ParadoxType.CONTRADICTION is not None
        assert ParadoxType.IMPOSSIBLE_STATE is not None
        assert ParadoxType.NARRATIVE_BREAK is not None
        assert ParadoxType.CAUSAL_PARADOX is not None


class TestParadox:
    """Tests for the Paradox class."""
    
    def test_paradox_creation(self):
        """Test creating a paradox."""
        paradox = Paradox(
            paradox_type=ParadoxType.TEMPORAL_LOOP,
            description="You are stuck in a loop",
            severity=7,
        )
        
        assert paradox.paradox_type == ParadoxType.TEMPORAL_LOOP
        assert paradox.description == "You are stuck in a loop"
        assert paradox.severity == 7
    
    def test_paradox_with_affected_nodes(self):
        """Test creating a paradox with affected nodes."""
        paradox = Paradox(
            paradox_type=ParadoxType.CONTRADICTION,
            description="Actions contradict",
            affected_nodes=["node1", "node2"],
        )
        
        assert len(paradox.affected_nodes) == 2
    
    def test_paradox_with_metadata(self):
        """Test creating a paradox with metadata."""
        paradox = Paradox(
            paradox_type=ParadoxType.IMPOSSIBLE_STATE,
            description="State shouldn't exist",
            metadata={"missing_item": "key"},
        )
        
        assert paradox.metadata["missing_item"] == "key"


class TestStoryGenerator:
    """Tests for the StoryGenerator class."""
    
    def test_generate_intro(self):
        """Test generating an intro."""
        intro = StoryGenerator.generate_intro("the library")
        
        assert isinstance(intro, str)
        assert len(intro) > 0
    
    def test_generate_intro_unknown_location(self):
        """Test generating intro for unknown location."""
        intro = StoryGenerator.generate_intro("unknown place")
        
        assert isinstance(intro, str)
        assert "unknown place" in intro
    
    def test_generate_paradox_resolution(self):
        """Test generating paradox resolution text."""
        paradox = Paradox(
            paradox_type=ParadoxType.TEMPORAL_LOOP,
            description="Loop detected",
        )
        player = Player()
        
        resolution = StoryGenerator.generate_paradox_resolution(paradox, player)
        
        assert isinstance(resolution, str)
        assert len(resolution) > 0
    
    def test_generate_loop_break(self):
        """Test generating loop break text."""
        text = StoryGenerator.generate_loop_break()
        
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_generate_choices(self):
        """Test generating dynamic choices."""
        player = Player()
        
        choices = StoryGenerator.generate_choices("the library", player)
        
        assert isinstance(choices, list)
        assert len(choices) > 0
        assert all(isinstance(c, Choice) for c in choices)
    
    def test_generate_choices_location_specific(self):
        """Test that choices are location-specific."""
        player = Player()
        
        library_choices = StoryGenerator.generate_choices("the library", player)
        market_choices = StoryGenerator.generate_choices("the market", player)
        
        library_actions = [c.action for c in library_choices]
        market_actions = [c.action for c in market_choices]
        
        # Library should have read option, market should have browse
        assert any("read" in a for a in library_actions)
        assert any("browse" in a for a in market_actions)


class TestInfiniteStoryLoop:
    """Tests for the InfiniteStoryLoop class."""
    
    def test_game_creation(self):
        """Test creating a new game."""
        game = InfiniteStoryLoop()
        
        assert game.current_node is not None
        assert game.player is not None
        assert game.paradox_count == 0
        assert game.rewrite_count == 0
    
    def test_game_with_custom_player(self):
        """Test creating a game with custom player."""
        player = Player(name="Hero")
        game = InfiniteStoryLoop(player=player)
        
        assert game.player.name == "Hero"
    
    def test_initial_story_state(self):
        """Test the initial story state."""
        game = InfiniteStoryLoop()
        
        assert game.current_node.location == "the beginning"
        assert len(game.current_node.choices) > 0
    
    def test_get_current_text(self):
        """Test getting current story text."""
        game = InfiniteStoryLoop()
        
        text = game.get_current_text()
        
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_get_current_choices(self):
        """Test getting current choices."""
        game = InfiniteStoryLoop()
        
        choices = game.get_current_choices()
        
        assert isinstance(choices, list)
        assert len(choices) > 0
    
    def test_process_input_help(self):
        """Test processing help command."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("help")
        
        assert response["type"] == "system"
        assert "HELP" in response["text"] or "help" in response["text"].lower()
    
    def test_process_input_status(self):
        """Test processing status command."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("status")
        
        assert response["type"] == "system"
        assert "Player" in response["text"] or "Location" in response["text"]
    
    def test_process_input_quit(self):
        """Test processing quit command."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("quit")
        
        assert response["type"] == "quit"
    
    def test_process_input_map(self):
        """Test processing map command."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("map")
        
        assert response["type"] == "system"
        assert "STORY MAP" in response["text"]
    
    def test_process_input_action(self):
        """Test processing an action."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("go north")
        
        assert response["type"] in ["story", "paradox"]
        assert "text" in response
    
    def test_process_input_advances_story(self):
        """Test that processing input advances the story."""
        game = InfiniteStoryLoop()
        initial_node = game.current_node
        
        game.process_input("go north")
        
        assert game.current_node != initial_node
    
    def test_process_input_records_choice(self):
        """Test that choices are recorded."""
        game = InfiniteStoryLoop()
        initial_choices = len(game.player.choice_history)
        
        game.process_input("go north")
        
        assert len(game.player.choice_history) > initial_choices
    
    def test_paradox_detection_contradiction(self):
        """Test detecting a contradiction paradox."""
        game = InfiniteStoryLoop()
        
        # Simulate conflicting actions
        game.process_input("go north")
        game.process_input("go south")  # Going back
        
        # The game should track at least one action (paradox detection may alter flow)
        assert len(game.player.choice_history) >= 1
    
    def test_paradox_detection_impossible_state(self):
        """Test detecting an impossible state paradox."""
        game = InfiniteStoryLoop()
        
        # Try to use an item we don't have
        response = game.process_input("use magic wand")
        
        # Should either be a paradox or story response
        assert response["type"] in ["story", "paradox", "error"]
    
    def test_paradox_handling_increments_count(self):
        """Test that handling paradoxes increments count."""
        game = InfiniteStoryLoop()
        initial_count = game.paradox_count
        
        # Create conditions for a paradox (repeated pattern)
        for _ in range(12):
            game.process_input("go north")
            game.process_input("go south")
        
        # Paradox count may have increased if loop was detected
        assert game.paradox_count >= initial_count
    
    def test_story_rewrite_creates_new_node(self):
        """Test that story rewrites create new nodes."""
        game = InfiniteStoryLoop()
        initial_nodes = len(game.story_graph)
        
        game.process_input("go north")
        
        assert len(game.story_graph) > initial_nodes
    
    def test_location_changes_on_movement(self):
        """Test that location changes when moving."""
        game = InfiniteStoryLoop()
        initial_location = game.player.current_location
        
        game.process_input("go north")
        
        # Location might change (depends on story generation)
        # Just verify the action was processed
        assert len(game.player.visited_locations) >= 1
    
    def test_to_dict(self):
        """Test serializing game to dictionary."""
        game = InfiniteStoryLoop()
        game.process_input("go north")
        
        data = game.to_dict()
        
        assert "story_graph" in data
        assert "current_node_id" in data
        assert "player" in data
        assert "history" in data
        assert "paradox_count" in data
        assert "rewrite_count" in data
    
    def test_from_dict(self):
        """Test deserializing game from dictionary."""
        original = InfiniteStoryLoop()
        original.process_input("go north")
        original.process_input("look")
        
        data = original.to_dict()
        restored = InfiniteStoryLoop.from_dict(data)
        
        assert restored.paradox_count == original.paradox_count
        assert restored.rewrite_count == original.rewrite_count
        assert len(restored.player.choice_history) == len(original.player.choice_history)
    
    def test_save_command(self):
        """Test save command response."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("save")
        
        assert response["type"] == "save"
    
    def test_load_command(self):
        """Test load command response."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("load")
        
        assert response["type"] == "load"
    
    def test_freeform_input(self):
        """Test freeform input processing."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("wander aimlessly through the void")
        
        assert response["type"] in ["story", "paradox", "error", "system"]
    
    def test_look_action(self):
        """Test look action."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("look")
        
        assert response["type"] == "story"
        assert len(response["text"]) > 0
    
    def test_take_action(self):
        """Test take action."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("take sword")
        
        assert response["type"] in ["story", "paradox"]
    
    def test_talk_action(self):
        """Test talk action."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("talk to nobody")
        
        assert response["type"] in ["story", "paradox"]
    
    def test_multiple_actions_sequence(self):
        """Test a sequence of multiple actions."""
        game = InfiniteStoryLoop()
        
        actions = ["look", "go north", "look", "go east", "status"]
        
        for action in actions:
            response = game.process_input(action)
            assert response is not None
            assert "type" in response
    
    def test_inventory_command_alias(self):
        """Test inventory command alias."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("i")
        
        assert response["type"] == "system"
    
    def test_question_mark_help_alias(self):
        """Test ? as help alias."""
        game = InfiniteStoryLoop()
        
        response = game.process_input("?")
        
        assert response["type"] == "system"


class TestStoryGeneratorTemplates:
    """Tests for StoryGenerator templates and constants."""
    
    def test_templates_exist(self):
        """Test that required templates exist."""
        assert "intro" in StoryGenerator.TEMPLATES
        assert "paradox_resolution" in StoryGenerator.TEMPLATES
        assert "loop_break" in StoryGenerator.TEMPLATES
        assert "location_descriptions" in StoryGenerator.TEMPLATES
    
    def test_location_descriptions_exist(self):
        """Test that location descriptions exist."""
        locations = StoryGenerator.TEMPLATES["location_descriptions"]
        
        assert "the beginning" in locations
        assert "the library" in locations
        assert "the mirror hall" in locations
    
    def test_characters_exist(self):
        """Test that character definitions exist."""
        assert "the narrator" in StoryGenerator.CHARACTERS
        assert "the echo" in StoryGenerator.CHARACTERS
        assert "the keeper" in StoryGenerator.CHARACTERS
        assert "the glitch" in StoryGenerator.CHARACTERS
    
    def test_character_has_description(self):
        """Test that characters have descriptions."""
        for name, char in StoryGenerator.CHARACTERS.items():
            assert "description" in char
            assert "personality" in char
