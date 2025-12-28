"""
Unit tests for the Player module.

Tests the Player class, CommandParser, and PlayerState including
input parsing, inventory management, and state tracking.
"""

import pytest
from src.player import Player, PlayerState, CommandParser


class TestCommandParser:
    """Tests for the CommandParser class."""
    
    def test_parse_simple_verb(self):
        """Test parsing a simple verb command."""
        result = CommandParser.parse("look")
        
        assert result["verb"] == "look"
        assert result["target"] is None
        assert result["is_command"] is False
    
    def test_parse_verb_with_target(self):
        """Test parsing a verb with target."""
        result = CommandParser.parse("take sword")
        
        assert result["verb"] == "take"
        assert result["target"] == "sword"
    
    def test_parse_verb_with_preposition(self):
        """Test parsing a verb with preposition."""
        result = CommandParser.parse("go to the north")
        
        assert result["verb"] == "go"
        assert result["target"] == "north"
    
    def test_parse_talk_to(self):
        """Test parsing talk to command."""
        result = CommandParser.parse("talk to the wizard")
        
        assert result["verb"] == "talk"
        assert result["target"] == "wizard"
    
    def test_parse_system_command(self):
        """Test parsing system commands."""
        result = CommandParser.parse("help")
        
        assert result["verb"] == "help"
        assert result["is_command"] is True
    
    def test_parse_status_command(self):
        """Test parsing status command."""
        result = CommandParser.parse("status")
        
        assert result["verb"] == "status"
        assert result["is_command"] is True
    
    def test_parse_quit_command(self):
        """Test parsing quit command."""
        result = CommandParser.parse("quit")
        
        assert result["verb"] == "quit"
        assert result["is_command"] is True
    
    def test_parse_inventory_alias(self):
        """Test parsing inventory alias."""
        result = CommandParser.parse("inv")
        
        assert result["verb"] == "status"
        assert result["is_command"] is True
    
    def test_parse_empty_input(self):
        """Test parsing empty input."""
        result = CommandParser.parse("")
        
        assert result["verb"] is None
        assert result["is_command"] is False
    
    def test_parse_freeform_input(self):
        """Test parsing freeform input without recognized verb."""
        result = CommandParser.parse("seeking answers in the void")
        
        assert result["verb"] == "freeform"
        assert "seeking" in result["target"]
    
    def test_parse_preserves_original(self):
        """Test that original input is preserved."""
        result = CommandParser.parse("Go To The NORTH")
        
        assert result["original"] == "Go To The NORTH"
    
    def test_parse_verb_aliases(self):
        """Test verb aliases are recognized."""
        walk = CommandParser.parse("walk north")
        move = CommandParser.parse("move north")
        travel = CommandParser.parse("travel north")
        
        assert walk["verb"] == "go"
        assert move["verb"] == "go"
        assert travel["verb"] == "go"
    
    def test_parse_take_aliases(self):
        """Test take verb aliases."""
        pick = CommandParser.parse("pick up sword")
        grab = CommandParser.parse("grab sword")
        collect = CommandParser.parse("collect coin")
        
        assert pick["verb"] == "take"
        assert grab["verb"] == "take"
        assert collect["verb"] == "take"
    
    def test_get_direction_north(self):
        """Test direction extraction for north."""
        assert CommandParser.get_direction("north") == "north"
        assert CommandParser.get_direction("n") == "north"
        assert CommandParser.get_direction("up") == "north"
    
    def test_get_direction_south(self):
        """Test direction extraction for south."""
        assert CommandParser.get_direction("south") == "south"
        assert CommandParser.get_direction("s") == "south"
        assert CommandParser.get_direction("down") == "south"
    
    def test_get_direction_east_west(self):
        """Test direction extraction for east and west."""
        assert CommandParser.get_direction("east") == "east"
        assert CommandParser.get_direction("e") == "east"
        assert CommandParser.get_direction("west") == "west"
        assert CommandParser.get_direction("w") == "west"
    
    def test_get_direction_compound(self):
        """Test compound direction extraction."""
        assert CommandParser.get_direction("northeast") == "northeast"
        assert CommandParser.get_direction("ne") == "northeast"
        assert CommandParser.get_direction("southwest") == "southwest"
    
    def test_get_direction_none(self):
        """Test direction extraction with None input."""
        assert CommandParser.get_direction(None) is None
    
    def test_get_direction_unknown(self):
        """Test direction extraction with unknown direction."""
        assert CommandParser.get_direction("somewhere") == "somewhere"


class TestPlayerState:
    """Tests for the PlayerState class."""
    
    def test_state_creation(self):
        """Test creating a player state."""
        state = PlayerState(
            location="forest",
            inventory=["sword", "shield"],
            visited_locations={"forest", "cave"},
            choice_count=5,
        )
        
        assert state.location == "forest"
        assert len(state.inventory) == 2
        assert len(state.visited_locations) == 2
        assert state.choice_count == 5
    
    def test_state_to_dict(self):
        """Test serializing state to dictionary."""
        state = PlayerState(
            location="castle",
            inventory=["key"],
            visited_locations={"castle"},
            choice_count=3,
        )
        
        data = state.to_dict()
        
        assert data["location"] == "castle"
        assert data["inventory"] == ["key"]
        assert "castle" in data["visited_locations"]
        assert data["choice_count"] == 3
    
    def test_state_from_dict(self):
        """Test deserializing state from dictionary."""
        data = {
            "location": "dungeon",
            "inventory": ["torch", "rope"],
            "visited_locations": ["dungeon", "entrance"],
            "choice_count": 10,
        }
        
        state = PlayerState.from_dict(data)
        
        assert state.location == "dungeon"
        assert len(state.inventory) == 2
        assert "dungeon" in state.visited_locations
        assert state.choice_count == 10


class TestPlayer:
    """Tests for the Player class."""
    
    def test_player_creation_defaults(self):
        """Test creating a player with defaults."""
        player = Player()
        
        assert player.name == "Traveler"
        assert len(player.inventory) == 0
        assert player.current_location == "the beginning"
    
    def test_player_creation_with_values(self):
        """Test creating a player with custom values."""
        player = Player(
            name="Hero",
            current_location="castle",
        )
        
        assert player.name == "Hero"
        assert player.current_location == "castle"
    
    def test_add_item(self):
        """Test adding an item to inventory."""
        player = Player()
        
        result = player.add_item("sword")
        
        assert result is True
        assert "sword" in player.inventory
    
    def test_add_item_duplicate(self):
        """Test adding a duplicate item."""
        player = Player()
        player.add_item("sword")
        
        result = player.add_item("sword")
        
        assert result is False
        assert player.inventory.count("sword") == 1
    
    def test_add_item_case_insensitive(self):
        """Test that item check is case-insensitive."""
        player = Player()
        player.add_item("Sword")
        
        result = player.add_item("sword")
        
        assert result is False
    
    def test_remove_item(self):
        """Test removing an item from inventory."""
        player = Player()
        player.add_item("sword")
        
        result = player.remove_item("sword")
        
        assert result is True
        assert "sword" not in player.inventory
    
    def test_remove_item_not_found(self):
        """Test removing a non-existent item."""
        player = Player()
        
        result = player.remove_item("shield")
        
        assert result is False
    
    def test_remove_item_case_insensitive(self):
        """Test that item removal is case-insensitive."""
        player = Player()
        player.add_item("Sword")
        
        result = player.remove_item("sword")
        
        assert result is True
    
    def test_has_item(self):
        """Test checking if player has an item."""
        player = Player()
        player.add_item("key")
        
        assert player.has_item("key") is True
        assert player.has_item("Key") is True
        assert player.has_item("lock") is False
    
    def test_move_to(self):
        """Test moving to a new location."""
        player = Player()
        
        player.move_to("forest")
        
        assert player.current_location == "forest"
        assert "forest" in player.visited_locations
    
    def test_visited_locations_tracked(self):
        """Test that visited locations are tracked."""
        player = Player()
        player.move_to("forest")
        player.move_to("cave")
        player.move_to("forest")  # Revisit
        
        assert len(player.visited_locations) == 3  # beginning + forest + cave
    
    def test_record_choice(self):
        """Test recording a player choice."""
        player = Player()
        
        player.record_choice("node-123", {"verb": "go", "target": "north"})
        
        assert len(player.choice_history) == 1
        assert len(player.action_history) == 1
        assert player.choice_history[0] == "node-123"
    
    def test_set_and_get_flag(self):
        """Test setting and getting flags."""
        player = Player()
        
        player.set_flag("has_talked_to_wizard", True)
        
        assert player.get_flag("has_talked_to_wizard") is True
        assert player.get_flag("unknown_flag") is False
    
    def test_flag_case_insensitive(self):
        """Test that flag access is case-insensitive."""
        player = Player()
        player.set_flag("MyFlag", True)
        
        assert player.get_flag("myflag") is True
        assert player.get_flag("MYFLAG") is True
    
    def test_set_and_get_variable(self):
        """Test setting and getting variables."""
        player = Player()
        
        player.set_variable("gold", 100)
        
        assert player.get_variable("gold") == 100
        assert player.get_variable("unknown", 0) == 0
    
    def test_get_status(self):
        """Test getting player status string."""
        player = Player(name="Hero")
        player.add_item("sword")
        player.move_to("castle")
        
        status = player.get_status()
        
        assert "Hero" in status
        assert "castle" in status
        assert "sword" in status
    
    def test_has_visited(self):
        """Test checking if location was visited."""
        player = Player()
        player.move_to("forest")
        
        assert player.has_visited("forest") is True
        assert player.has_visited("FOREST") is True
        assert player.has_visited("cave") is False
    
    def test_get_action_pattern(self):
        """Test getting action pattern."""
        player = Player()
        player.record_choice("n1", {"verb": "go"})
        player.record_choice("n2", {"verb": "take"})
        player.record_choice("n3", {"verb": "go"})
        
        pattern = player.get_action_pattern()
        
        assert pattern == ["go", "take", "go"]
    
    def test_detect_action_loop_found(self):
        """Test detecting an action loop."""
        player = Player()
        
        # Create a repeating pattern
        for _ in range(2):
            player.record_choice("n1", {"verb": "go"})
            player.record_choice("n2", {"verb": "look"})
            player.record_choice("n3", {"verb": "take"})
            player.record_choice("n4", {"verb": "go"})
            player.record_choice("n5", {"verb": "look"})
        
        loop = player.detect_action_loop(window_size=5)
        
        assert loop is not None
        assert loop == ["go", "look", "take", "go", "look"]
    
    def test_detect_action_loop_not_found(self):
        """Test when no loop is detected."""
        player = Player()
        player.record_choice("n1", {"verb": "go"})
        player.record_choice("n2", {"verb": "look"})
        player.record_choice("n3", {"verb": "take"})
        
        loop = player.detect_action_loop()
        
        assert loop is None
    
    def test_to_dict(self):
        """Test serializing player to dictionary."""
        player = Player(name="Hero")
        player.add_item("sword")
        player.move_to("castle")
        player.set_flag("test_flag", True)
        
        data = player.to_dict()
        
        assert data["name"] == "Hero"
        assert "sword" in data["inventory"]
        assert data["current_location"] == "castle"
        assert data["flags"]["test_flag"] is True
    
    def test_from_dict(self):
        """Test deserializing player from dictionary."""
        data = {
            "name": "Hero",
            "inventory": ["sword", "shield"],
            "current_location": "forest",
            "visited_locations": ["forest", "cave"],
            "choice_history": ["n1", "n2"],
            "action_history": [{"verb": "go"}],
            "flags": {"found_key": True},
            "variables": {"gold": 50},
            "state_history": [],
        }
        
        player = Player.from_dict(data)
        
        assert player.name == "Hero"
        assert len(player.inventory) == 2
        assert player.current_location == "forest"
        assert player.get_flag("found_key") is True
        assert player.get_variable("gold") == 50
    
    def test_str_representation(self):
        """Test string representation of player."""
        player = Player(name="Test")
        player.add_item("item1")
        
        str_repr = str(player)
        
        assert "Test" in str_repr
        assert "1" in str_repr  # Item count
    
    def test_state_history_tracked(self):
        """Test that state history is tracked."""
        player = Player()
        initial_history_length = len(player.state_history)
        
        player.move_to("forest")
        player.move_to("cave")
        
        assert len(player.state_history) > initial_history_length
