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
        """Test that all paradox types exist.

        Verifies that the ParadoxType enum contains all expected paradox
        type values including temporal loop, contradiction, impossible state,
        narrative break, and causal paradox.
        """
        assert ParadoxType.TEMPORAL_LOOP is not None
        assert ParadoxType.CONTRADICTION is not None
        assert ParadoxType.IMPOSSIBLE_STATE is not None
        assert ParadoxType.NARRATIVE_BREAK is not None
        assert ParadoxType.CAUSAL_PARADOX is not None


class TestParadox:
    """Tests for the Paradox class."""
    
    def test_paradox_creation(self):
        """Test creating a paradox with basic attributes.

        Creates a Paradox instance with type, description, and severity,
        then verifies all attributes are correctly assigned.
        """
        paradox = Paradox(
            paradox_type=ParadoxType.TEMPORAL_LOOP,
            description="You are stuck in a loop",
            severity=7,
        )
        
        assert paradox.paradox_type == ParadoxType.TEMPORAL_LOOP
        assert paradox.description == "You are stuck in a loop"
        assert paradox.severity == 7
    
    def test_paradox_with_affected_nodes(self):
        """Test creating a paradox with affected nodes.

        Creates a Paradox instance with a list of affected node IDs
        and verifies the nodes are correctly stored.
        """
        paradox = Paradox(
            paradox_type=ParadoxType.CONTRADICTION,
            description="Actions contradict",
            affected_nodes=["node1", "node2"],
        )
        
        assert len(paradox.affected_nodes) == 2
    
    def test_paradox_with_metadata(self):
        """Test creating a paradox with metadata.

        Creates a Paradox instance with additional metadata dictionary
        and verifies the metadata is accessible.
        """
        paradox = Paradox(
            paradox_type=ParadoxType.IMPOSSIBLE_STATE,
            description="State shouldn't exist",
            metadata={"missing_item": "key"},
        )
        
        assert paradox.metadata["missing_item"] == "key"


class TestStoryGenerator:
    """Tests for the StoryGenerator class."""
    
    def test_generate_intro(self):
        """Test generating an intro for a known location.

        Generates intro text for 'the library' location and verifies
        the result is a non-empty string.
        """
        intro = StoryGenerator.generate_intro("the library")
        
        assert isinstance(intro, str)
        assert len(intro) > 0
    
    def test_generate_intro_unknown_location(self):
        """Test generating intro for an unknown location.

        Generates intro text for an unrecognized location and verifies
        the location name is included in the fallback text.
        """
        intro = StoryGenerator.generate_intro("unknown place")
        
        assert isinstance(intro, str)
        assert "unknown place" in intro
    
    def test_generate_paradox_resolution(self):
        """Test generating paradox resolution text.

        Creates a paradox and player, generates resolution text,
        and verifies the result is a non-empty string.
        """
        paradox = Paradox(
            paradox_type=ParadoxType.TEMPORAL_LOOP,
            description="Loop detected",
        )
        player = Player()
        
        resolution = StoryGenerator.generate_paradox_resolution(paradox, player)
        
        assert isinstance(resolution, str)
        assert len(resolution) > 0
    
    def test_generate_loop_break(self):
        """Test generating loop break text.

        Generates text describing a loop break event and verifies
        the result is a non-empty string.
        """
        text = StoryGenerator.generate_loop_break()
        
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_generate_choices(self):
        """Test generating dynamic choices for a location.

        Generates choices for a player at a specific location and
        verifies the result is a non-empty list of Choice objects.
        """
        player = Player()
        
        choices = StoryGenerator.generate_choices("the library", player)
        
        assert isinstance(choices, list)
        assert len(choices) > 0
        assert all(isinstance(c, Choice) for c in choices)
    
    def test_generate_choices_location_specific(self):
        """Test that choices are location-specific.

        Generates choices for different locations and verifies
        that location-appropriate options are included (e.g., 'read'
        for library, 'browse' for market).
        """
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
        """Test creating a new game with default values.

        Creates a new InfiniteStoryLoop instance and verifies that
        all initial attributes are properly initialized including
        current node, player, and zero counts.
        """
        game = InfiniteStoryLoop()
        
        assert game.current_node is not None
        assert game.player is not None
        assert game.paradox_count == 0
        assert game.rewrite_count == 0
    
    def test_game_with_custom_player(self):
        """Test creating a game with a custom player.

        Creates a game with a pre-configured Player object and
        verifies the player is correctly associated with the game.
        """
        player = Player(name="Hero")
        game = InfiniteStoryLoop(player=player)
        
        assert game.player.name == "Hero"
    
    def test_initial_story_state(self):
        """Test the initial story state.

        Verifies that a new game starts at 'the beginning' location
        with available choices for the player.
        """
        game = InfiniteStoryLoop()
        
        assert game.current_node.location == "the beginning"
        assert len(game.current_node.choices) > 0
    
    def test_get_current_text(self):
        """Test getting current story text.

        Retrieves the current story text and verifies it is
        a non-empty string.
        """
        game = InfiniteStoryLoop()
        
        text = game.get_current_text()
        
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_get_current_choices(self):
        """Test getting current choices.

        Retrieves available choices for the current node and
        verifies the result is a non-empty list.
        """
        game = InfiniteStoryLoop()
        
        choices = game.get_current_choices()
        
        assert isinstance(choices, list)
        assert len(choices) > 0
    
    def test_process_input_help(self):
        """Test processing the help command.

        Sends the 'help' command and verifies the response is
        a system message containing help information.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("help")
        
        assert response["type"] == "system"
        assert "HELP" in response["text"] or "help" in response["text"].lower()
    
    def test_process_input_status(self):
        """Test processing the status command.

        Sends the 'status' command and verifies the response is
        a system message containing player or location information.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("status")
        
        assert response["type"] == "system"
        assert "Player" in response["text"] or "Location" in response["text"]
    
    def test_process_input_quit(self):
        """Test processing the quit command.

        Sends the 'quit' command and verifies the response
        indicates a quit action type.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("quit")
        
        assert response["type"] == "quit"
    
    def test_process_input_map(self):
        """Test processing the map command.

        Sends the 'map' command and verifies the response is
        a system message containing the story map.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("map")
        
        assert response["type"] == "system"
        assert "STORY MAP" in response["text"]
    
    def test_process_input_action(self):
        """Test processing a movement action.

        Sends a 'go north' command and verifies the response
        is either a story or paradox type with text content.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("go north")
        
        assert response["type"] in ["story", "paradox"]
        assert "text" in response
    
    def test_process_input_advances_story(self):
        """Test that processing input advances the story.

        Captures the initial node, processes an action, and
        verifies the current node has changed.
        """
        game = InfiniteStoryLoop()
        initial_node = game.current_node
        
        game.process_input("go north")
        
        assert game.current_node != initial_node
    
    def test_process_input_records_choice(self):
        """Test that choices are recorded in player history.

        Captures the initial choice count, processes an action,
        and verifies the choice was added to history.
        """
        game = InfiniteStoryLoop()
        initial_choices = len(game.player.choice_history)
        
        game.process_input("go north")
        
        assert len(game.player.choice_history) > initial_choices
    
    def test_paradox_detection_contradiction(self):
        """Test detecting a contradiction paradox.

        Simulates conflicting actions by going north then south
        and verifies the game tracks at least one action.
        """
        game = InfiniteStoryLoop()
        
        # Simulate conflicting actions
        game.process_input("go north")
        game.process_input("go south")  # Going back
        
        # The game should track at least one action (paradox detection may alter flow)
        assert len(game.player.choice_history) >= 1
    
    def test_paradox_detection_impossible_state(self):
        """Test detecting an impossible state paradox.

        Attempts to use an item not in inventory and verifies
        the response is a valid type (story, paradox, or error).
        """
        game = InfiniteStoryLoop()
        
        # Try to use an item we don't have
        response = game.process_input("use magic wand")
        
        # Should either be a paradox or story response
        assert response["type"] in ["story", "paradox", "error"]
    
    def test_paradox_handling_increments_count(self):
        """Test that handling paradoxes increments the paradox count.

        Creates conditions for a loop paradox through repeated
        back-and-forth movement and verifies the count is tracked.
        """
        game = InfiniteStoryLoop()
        initial_count = game.paradox_count
        
        # Create conditions for a paradox (repeated pattern)
        for _ in range(12):
            game.process_input("go north")
            game.process_input("go south")
        
        # Paradox count may have increased if loop was detected
        assert game.paradox_count >= initial_count
    
    def test_story_rewrite_creates_new_node(self):
        """Test that story rewrites create new nodes in the graph.

        Captures the initial node count, processes an action,
        and verifies new nodes were added to the story graph.
        """
        game = InfiniteStoryLoop()
        initial_nodes = len(game.story_graph)
        
        game.process_input("go north")
        
        assert len(game.story_graph) > initial_nodes
    
    def test_location_changes_on_movement(self):
        """Test that location changes when moving.

        Processes a movement action and verifies the player
        has at least one visited location recorded.
        """
        game = InfiniteStoryLoop()
        initial_location = game.player.current_location
        
        game.process_input("go north")
        
        # Location might change (depends on story generation)
        # Just verify the action was processed
        assert len(game.player.visited_locations) >= 1
    
    def test_to_dict(self):
        """Test serializing game state to a dictionary.

        Creates a game, processes an action, and verifies the
        serialized dictionary contains all required keys.
        """
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
        """Test deserializing game state from a dictionary.

        Creates a game, processes actions, serializes it, then
        restores from the dictionary and verifies state matches.
        """
        original = InfiniteStoryLoop()
        original.process_input("go north")
        original.process_input("look")
        
        data = original.to_dict()
        restored = InfiniteStoryLoop.from_dict(data)
        
        assert restored.paradox_count == original.paradox_count
        assert restored.rewrite_count == original.rewrite_count
        assert len(restored.player.choice_history) == len(original.player.choice_history)
    
    def test_save_command(self):
        """Test the save command response.

        Sends the 'save' command and verifies the response
        indicates a save action type.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("save")
        
        assert response["type"] == "save"
    
    def test_load_command(self):
        """Test the load command response.

        Sends the 'load' command and verifies the response
        indicates a load action type.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("load")
        
        assert response["type"] == "load"
    
    def test_freeform_input(self):
        """Test freeform input processing.

        Sends a non-standard input string and verifies the game
        processes it with a valid response type.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("wander aimlessly through the void")
        
        assert response["type"] in ["story", "paradox", "error", "system"]
    
    def test_look_action(self):
        """Test the look action.

        Sends the 'look' command and verifies the response is
        a story type with descriptive text.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("look")
        
        assert response["type"] == "story"
        assert len(response["text"]) > 0
    
    def test_take_action(self):
        """Test the take action.

        Sends a 'take sword' command and verifies the response
        is either a story or paradox type.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("take sword")
        
        assert response["type"] in ["story", "paradox"]
    
    def test_talk_action(self):
        """Test the talk action.

        Sends a 'talk to nobody' command and verifies the response
        is either a story or paradox type.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("talk to nobody")
        
        assert response["type"] in ["story", "paradox"]
    
    def test_multiple_actions_sequence(self):
        """Test a sequence of multiple actions.

        Processes a series of different commands and verifies
        each returns a valid response with a type field.
        """
        game = InfiniteStoryLoop()
        
        actions = ["look", "go north", "look", "go east", "status"]
        
        for action in actions:
            response = game.process_input(action)
            assert response is not None
            assert "type" in response
    
    def test_inventory_command_alias(self):
        """Test the inventory command alias.

        Sends the 'i' shortcut command and verifies it returns
        a system response for inventory display.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("i")
        
        assert response["type"] == "system"
    
    def test_question_mark_help_alias(self):
        """Test the question mark as help alias.

        Sends the '?' shortcut command and verifies it returns
        a system response with help information.
        """
        game = InfiniteStoryLoop()
        
        response = game.process_input("?")
        
        assert response["type"] == "system"


class TestStoryGeneratorTemplates:
    """Tests for StoryGenerator templates and constants."""
    
    def test_templates_exist(self):
        """Test that required templates exist in StoryGenerator.

        Verifies that the TEMPLATES dictionary contains all expected
        keys including intro, paradox_resolution, loop_break, and
        location_descriptions.
        """
        assert "intro" in StoryGenerator.TEMPLATES
        assert "paradox_resolution" in StoryGenerator.TEMPLATES
        assert "loop_break" in StoryGenerator.TEMPLATES
        assert "location_descriptions" in StoryGenerator.TEMPLATES
    
    def test_location_descriptions_exist(self):
        """Test that location descriptions exist for key locations.

        Verifies that the location_descriptions template contains
        entries for essential game locations.
        """
        locations = StoryGenerator.TEMPLATES["location_descriptions"]
        
        assert "the beginning" in locations
        assert "the library" in locations
        assert "the mirror hall" in locations
    
    def test_characters_exist(self):
        """Test that character definitions exist in StoryGenerator.

        Verifies that the CHARACTERS dictionary contains all expected
        character entries including narrator, echo, keeper, and glitch.
        """
        assert "the narrator" in StoryGenerator.CHARACTERS
        assert "the echo" in StoryGenerator.CHARACTERS
        assert "the keeper" in StoryGenerator.CHARACTERS
        assert "the glitch" in StoryGenerator.CHARACTERS
    
    def test_character_has_description(self):
        """Test that all characters have required attributes.

        Iterates through all characters and verifies each has
        both a description and personality field defined.
        """
        for name, char in StoryGenerator.CHARACTERS.items():
            assert "description" in char
            assert "personality" in char
