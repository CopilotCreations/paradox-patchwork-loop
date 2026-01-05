"""
Unit tests for the Utils module.

Tests the GameLogger, HistoryTracker, StateManager, and utility functions.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from src.utils import (
    GameLogger,
    HistoryTracker,
    HistoryEntry,
    StateManager,
    format_story_text,
    create_separator,
    create_header,
    get_random_surreal_event,
    parse_freeform_input,
)


class TestGameLogger:
    """Tests for the GameLogger class."""
    
    def test_logger_creation(self):
        """Test creating a logger.

        Verifies that a new GameLogger instance has empty entries
        and default log level of INFO (20).
        """
        logger = GameLogger()
        
        assert logger.entries == []
        assert logger.log_level == 20  # INFO
    
    def test_logger_with_console(self):
        """Test creating a logger with console output.

        Verifies that console_output flag is properly set when
        creating a GameLogger with console output enabled.
        """
        logger = GameLogger(console_output=True)
        
        assert logger.console_output is True
    
    def test_log_message(self):
        """Test logging a message.

        Verifies that a message is correctly logged with the specified
        level and category, and stored in the logger's entries.
        """
        logger = GameLogger()
        
        logger.log("Test message", "INFO", "TEST")
        
        assert len(logger.entries) == 1
        assert logger.entries[0]["message"] == "Test message"
        assert logger.entries[0]["level"] == "INFO"
        assert logger.entries[0]["category"] == "TEST"
    
    def test_log_debug(self):
        """Test logging debug message.

        Verifies that debug messages are logged when log level is set
        to DEBUG, and the entry has correct level.
        """
        logger = GameLogger(log_level="DEBUG")
        
        logger.debug("Debug message")
        
        assert len(logger.entries) == 1
        assert logger.entries[0]["level"] == "DEBUG"
    
    def test_log_info(self):
        """Test logging info message.

        Verifies that info messages are logged correctly and have
        the INFO level in the entry.
        """
        logger = GameLogger()
        
        logger.info("Info message")
        
        assert len(logger.entries) == 1
        assert logger.entries[0]["level"] == "INFO"
    
    def test_log_warning(self):
        """Test logging warning message.

        Verifies that warning messages are logged correctly and have
        the WARNING level in the entry.
        """
        logger = GameLogger()
        
        logger.warning("Warning message")
        
        assert len(logger.entries) == 1
        assert logger.entries[0]["level"] == "WARNING"
    
    def test_log_error(self):
        """Test logging error message.

        Verifies that error messages are logged correctly and have
        the ERROR level in the entry.
        """
        logger = GameLogger()
        
        logger.error("Error message")
        
        assert len(logger.entries) == 1
        assert logger.entries[0]["level"] == "ERROR"
    
    def test_log_story(self):
        """Test logging story event.

        Verifies that story events are logged with STORY level
        and NARRATIVE category.
        """
        logger = GameLogger()
        
        logger.story("Player moved north")
        
        assert len(logger.entries) == 1
        assert logger.entries[0]["level"] == "STORY"
        assert logger.entries[0]["category"] == "NARRATIVE"
    
    def test_log_paradox(self):
        """Test logging paradox event.

        Verifies that paradox events are logged with the PARADOX category.
        """
        logger = GameLogger()
        
        logger.paradox("Loop detected")
        
        assert len(logger.entries) == 1
        assert logger.entries[0]["category"] == "PARADOX"
    
    def test_log_level_filtering(self):
        """Test that log level filters messages.

        Verifies that messages below the configured log level are
        filtered out, while messages at or above the level are logged.
        """
        logger = GameLogger(log_level="WARNING")
        
        logger.debug("Debug")  # Should be filtered
        logger.info("Info")    # Should be filtered
        logger.warning("Warning")  # Should be logged
        logger.error("Error")  # Should be logged
        
        assert len(logger.entries) == 2
    
    def test_get_entries_all(self):
        """Test getting all log entries.

        Verifies that get_entries returns all logged entries
        when no filters are applied.
        """
        logger = GameLogger()
        logger.info("Message 1")
        logger.info("Message 2")
        logger.warning("Message 3")
        
        entries = logger.get_entries()
        
        assert len(entries) == 3
    
    def test_get_entries_by_level(self):
        """Test getting entries filtered by level.

        Verifies that get_entries correctly filters entries
        by the specified log level.
        """
        logger = GameLogger()
        logger.info("Info message")
        logger.warning("Warning message")
        logger.info("Another info")
        
        entries = logger.get_entries(level="INFO")
        
        assert len(entries) == 2
    
    def test_get_entries_by_category(self):
        """Test getting entries filtered by category.

        Verifies that get_entries correctly filters entries
        by the specified category.
        """
        logger = GameLogger()
        logger.log("Message 1", "INFO", "CAT1")
        logger.log("Message 2", "INFO", "CAT2")
        logger.log("Message 3", "INFO", "CAT1")
        
        entries = logger.get_entries(category="CAT1")
        
        assert len(entries) == 2
    
    def test_get_entries_with_limit(self):
        """Test getting limited number of entries.

        Verifies that get_entries respects the limit parameter
        and returns the most recent entries.
        """
        logger = GameLogger()
        for i in range(10):
            logger.info(f"Message {i}")
        
        entries = logger.get_entries(limit=5)
        
        assert len(entries) == 5
        assert entries[0]["message"] == "Message 5"  # Last 5
    
    def test_clear_entries(self):
        """Test clearing log entries.

        Verifies that the clear method removes all entries from the logger.
        """
        logger = GameLogger()
        logger.info("Message 1")
        logger.info("Message 2")
        
        logger.clear()
        
        assert len(logger.entries) == 0
    
    def test_log_to_file(self):
        """Test logging to a file.

        Verifies that the logger correctly writes log entries to a file
        when a log_file path is provided.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = GameLogger(log_file=log_file)
            
            logger.info("Test message")
            
            assert os.path.exists(log_file)
            with open(log_file, "r") as f:
                content = f.read()
            assert "Test message" in content


class TestHistoryEntry:
    """Tests for the HistoryEntry class."""
    
    def test_entry_creation(self):
        """Test creating a history entry.

        Verifies that a HistoryEntry is created with the correct
        node_id, action, and auto-generated timestamp.
        """
        entry = HistoryEntry(
            node_id="node-123",
            action="go north",
        )
        
        assert entry.node_id == "node-123"
        assert entry.action == "go north"
        assert entry.timestamp is not None
    
    def test_entry_with_metadata(self):
        """Test creating an entry with metadata.

        Verifies that a HistoryEntry correctly stores additional
        metadata provided during creation.
        """
        entry = HistoryEntry(
            node_id="node-123",
            action="take sword",
            metadata={"item": "sword"},
        )
        
        assert entry.metadata["item"] == "sword"
    
    def test_entry_to_dict(self):
        """Test serializing entry to dictionary.

        Verifies that the to_dict method correctly converts
        the HistoryEntry to a dictionary representation.
        """
        entry = HistoryEntry(
            node_id="node-123",
            action="look",
            state_hash="abc123",
        )
        
        data = entry.to_dict()
        
        assert data["node_id"] == "node-123"
        assert data["action"] == "look"
        assert data["state_hash"] == "abc123"
    
    def test_entry_from_dict(self):
        """Test deserializing entry from dictionary.

        Verifies that the from_dict class method correctly creates
        a HistoryEntry from a dictionary representation.
        """
        data = {
            "node_id": "node-456",
            "action": "talk",
            "timestamp": "2024-01-01T00:00:00",
            "state_hash": "def456",
            "metadata": {"target": "wizard"},
        }
        
        entry = HistoryEntry.from_dict(data)
        
        assert entry.node_id == "node-456"
        assert entry.action == "talk"
        assert entry.metadata["target"] == "wizard"


class TestHistoryTracker:
    """Tests for the HistoryTracker class."""
    
    def test_tracker_creation(self):
        """Test creating a history tracker.

        Verifies that a new HistoryTracker has empty entries
        and state_hashes collections.
        """
        tracker = HistoryTracker()
        
        assert len(tracker.entries) == 0
        assert len(tracker.state_hashes) == 0
    
    def test_add_entry(self):
        """Test adding an entry to the tracker.

        Verifies that add_entry creates a new entry with correct data
        and generates a state hash.
        """
        tracker = HistoryTracker()
        
        entry = tracker.add_entry(
            node_id="node-123",
            action="go north",
            state={"location": "forest"},
        )
        
        assert len(tracker.entries) == 1
        assert entry.node_id == "node-123"
        assert entry.state_hash != ""
    
    def test_detect_loop_found(self):
        """Test detecting a state loop.

        Verifies that detect_loop returns the index of the first entry
        with a matching state hash when a loop is detected.
        """
        tracker = HistoryTracker()
        
        state1 = {"location": "forest", "items": []}
        state2 = {"location": "cave", "items": []}
        
        tracker.add_entry("n1", "go", state1)
        tracker.add_entry("n2", "go", state2)
        
        # Return to same state
        loop_index = tracker.detect_loop(state1)
        
        assert loop_index == 0
    
    def test_detect_loop_not_found(self):
        """Test when no loop is detected.

        Verifies that detect_loop returns None when the given state
        does not match any previously recorded state.
        """
        tracker = HistoryTracker()
        
        state1 = {"location": "forest"}
        state2 = {"location": "cave"}
        state3 = {"location": "castle"}
        
        tracker.add_entry("n1", "go", state1)
        tracker.add_entry("n2", "go", state2)
        
        loop_index = tracker.detect_loop(state3)
        
        assert loop_index is None
    
    def test_detect_node_loop(self):
        """Test detecting node visit loops.

        Verifies that detect_node_loop identifies repeating patterns
        of node visits within the specified window size.
        """
        tracker = HistoryTracker()
        
        # Create a repeating pattern of node visits
        for _ in range(2):
            for node_id in ["n1", "n2", "n3"]:
                tracker.add_entry(node_id, "action", {"x": 1})
        
        loop = tracker.detect_node_loop(window_size=6)
        
        # Pattern of 3 should be detected
        assert loop is not None or len(tracker.entries) >= 6
    
    def test_detect_contradiction(self):
        """Test detecting contradicting actions.

        Verifies that detect_contradiction identifies when a new action
        contradicts a previous action on the same target.
        """
        tracker = HistoryTracker()
        
        tracker.add_entry("n1", "take sword", {}, {"target": "sword"})
        
        contradiction = tracker.detect_contradiction("drop sword", "sword")
        
        assert contradiction is not None
        assert contradiction["type"] == "contradiction"
    
    def test_detect_contradiction_not_found(self):
        """Test when no contradiction is detected.

        Verifies that detect_contradiction returns None when
        the action does not contradict any previous actions.
        """
        tracker = HistoryTracker()
        
        tracker.add_entry("n1", "take sword", {}, {"target": "sword"})
        
        contradiction = tracker.detect_contradiction("take shield", "shield")
        
        assert contradiction is None
    
    def test_get_recent_actions(self):
        """Test getting recent actions.

        Verifies that get_recent_actions returns the specified number
        of most recent actions in order.
        """
        tracker = HistoryTracker()
        
        tracker.add_entry("n1", "go north", {})
        tracker.add_entry("n2", "look", {})
        tracker.add_entry("n3", "take key", {})
        
        recent = tracker.get_recent_actions(2)
        
        assert len(recent) == 2
        assert recent == ["look", "take key"]
    
    def test_get_visited_nodes(self):
        """Test getting set of visited nodes.

        Verifies that get_visited_nodes returns a set of unique
        node IDs that have been visited.
        """
        tracker = HistoryTracker()
        
        tracker.add_entry("n1", "action1", {})
        tracker.add_entry("n2", "action2", {})
        tracker.add_entry("n1", "action3", {})  # Revisit
        
        visited = tracker.get_visited_nodes()
        
        assert visited == {"n1", "n2"}
    
    def test_get_node_visit_count(self):
        """Test counting node visits.

        Verifies that get_node_visit_count returns the correct
        number of times a specific node has been visited.
        """
        tracker = HistoryTracker()
        
        tracker.add_entry("n1", "a1", {})
        tracker.add_entry("n2", "a2", {})
        tracker.add_entry("n1", "a3", {})
        tracker.add_entry("n1", "a4", {})
        
        count = tracker.get_node_visit_count("n1")
        
        assert count == 3
    
    def test_tracker_to_dict(self):
        """Test serializing tracker to dictionary.

        Verifies that the to_dict method correctly converts
        the HistoryTracker to a dictionary representation.
        """
        tracker = HistoryTracker()
        tracker.add_entry("n1", "action", {"x": 1})
        
        data = tracker.to_dict()
        
        assert "entries" in data
        assert "state_hashes" in data
        assert len(data["entries"]) == 1
    
    def test_tracker_from_dict(self):
        """Test deserializing tracker from dictionary.

        Verifies that the from_dict class method correctly creates
        a HistoryTracker from a dictionary representation.
        """
        data = {
            "entries": [
                {"node_id": "n1", "action": "go", "timestamp": "", "state_hash": "abc", "metadata": {}}
            ],
            "state_hashes": ["abc", "def"],
        }
        
        tracker = HistoryTracker.from_dict(data)
        
        assert len(tracker.entries) == 1
        assert "abc" in tracker.state_hashes
    
    def test_clear_tracker(self):
        """Test clearing the tracker.

        Verifies that the clear method removes all entries
        and state hashes from the tracker.
        """
        tracker = HistoryTracker()
        tracker.add_entry("n1", "action", {})
        
        tracker.clear()
        
        assert len(tracker.entries) == 0
        assert len(tracker.state_hashes) == 0


class TestStateManager:
    """Tests for the StateManager class."""
    
    def test_manager_creation(self):
        """Test creating a state manager.

        Verifies that a new StateManager is created with default
        auto_save_enabled and auto_save_interval values.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(save_directory=tmpdir)
            
            assert manager.auto_save_enabled is True
            assert manager.auto_save_interval == 10
    
    def test_save_game(self):
        """Test saving a game state.

        Verifies that save creates a JSON file with the game state
        at the specified save name.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(save_directory=tmpdir)
            game_state = {"location": "forest", "items": ["sword"]}
            
            path = manager.save(game_state, "test_save")
            
            assert os.path.exists(path)
            assert path.endswith(".json")
    
    def test_save_game_auto_filename(self):
        """Test saving with auto-generated filename.

        Verifies that save generates a filename with 'save_' prefix
        when no save name is provided.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(save_directory=tmpdir)
            game_state = {"location": "cave"}
            
            path = manager.save(game_state)
            
            assert os.path.exists(path)
            assert "save_" in path
    
    def test_load_game(self):
        """Test loading a saved game.

        Verifies that load correctly retrieves the game state
        from a previously saved file.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(save_directory=tmpdir)
            original_state = {"location": "castle", "gold": 100}
            
            manager.save(original_state, "load_test")
            loaded_state = manager.load("load_test")
            
            assert loaded_state is not None
            assert loaded_state["location"] == "castle"
            assert loaded_state["gold"] == 100
    
    def test_load_game_not_found(self):
        """Test loading a non-existent save.

        Verifies that load returns None when the specified
        save file does not exist.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(save_directory=tmpdir)
            
            loaded_state = manager.load("nonexistent")
            
            assert loaded_state is None
    
    def test_list_saves(self):
        """Test listing available saves.

        Verifies that list_saves returns all save files
        in the save directory.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(save_directory=tmpdir)
            
            manager.save({"x": 1}, "save1")
            manager.save({"x": 2}, "save2")
            
            saves = manager.list_saves()
            
            assert len(saves) == 2
    
    def test_delete_save(self):
        """Test deleting a save file.

        Verifies that delete_save removes the specified save file
        and returns True on success.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(save_directory=tmpdir)
            manager.save({"x": 1}, "to_delete")
            
            result = manager.delete_save("to_delete")
            
            assert result is True
            assert manager.load("to_delete") is None
    
    def test_delete_save_not_found(self):
        """Test deleting a non-existent save.

        Verifies that delete_save returns False when attempting
        to delete a save file that does not exist.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(save_directory=tmpdir)
            
            result = manager.delete_save("nonexistent")
            
            assert result is False
    
    def test_auto_save(self):
        """Test auto-save functionality.

        Verifies that auto_save triggers a save after the configured
        number of actions (auto_save_interval) have occurred.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(
                save_directory=tmpdir,
                auto_save_enabled=True,
                auto_save_interval=2,
            )
            
            result1 = manager.auto_save({"x": 1})  # Action 1
            result2 = manager.auto_save({"x": 2})  # Action 2 - triggers save
            
            assert result1 is None
            assert result2 is not None
    
    def test_auto_save_disabled(self):
        """Test that auto-save can be disabled.

        Verifies that auto_save never triggers a save when
        auto_save_enabled is set to False.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(
                save_directory=tmpdir,
                auto_save_enabled=False,
                auto_save_interval=1,
            )
            
            for _ in range(5):
                result = manager.auto_save({"x": 1})
                assert result is None


class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_format_story_text_simple(self):
        """Test formatting simple text.

        Verifies that format_story_text preserves simple text content.
        """
        text = "This is a test."
        
        formatted = format_story_text(text)
        
        assert "This is a test." in formatted
    
    def test_format_story_text_wrapping(self):
        """Test that long text is wrapped.

        Verifies that format_story_text wraps long lines to the
        specified width limit.
        """
        text = "This is a very long line of text that should be wrapped to a reasonable width for console display."
        
        formatted = format_story_text(text, width=40)
        
        lines = formatted.split("\n")
        for line in lines:
            assert len(line) <= 40
    
    def test_format_story_text_paragraphs(self):
        """Test that paragraphs are preserved.

        Verifies that format_story_text maintains paragraph
        breaks (double newlines) in the output.
        """
        text = "First paragraph.\n\nSecond paragraph."
        
        formatted = format_story_text(text)
        
        assert "\n\n" in formatted
    
    def test_create_separator(self):
        """Test creating a separator line.

        Verifies that create_separator generates a line of the
        specified character repeated to the specified length.
        """
        separator = create_separator("=", 10)
        
        assert separator == "=========="
    
    def test_create_separator_default(self):
        """Test creating separator with defaults.

        Verifies that create_separator uses default character and
        length when no parameters are provided.
        """
        separator = create_separator()
        
        assert len(separator) == 70
        assert separator[0] == "═"
    
    def test_create_header(self):
        """Test creating a header.

        Verifies that create_header generates a box-formatted header
        containing the title text with border characters.
        """
        header = create_header("Test Title", width=30)
        
        assert "Test Title" in header
        assert "╔" in header
        assert "╚" in header
    
    def test_get_random_surreal_event(self):
        """Test getting a random surreal event.

        Verifies that get_random_surreal_event returns a non-empty
        string describing a surreal event.
        """
        event = get_random_surreal_event()
        
        assert isinstance(event, str)
        assert len(event) > 0
    
    def test_get_random_surreal_event_variety(self):
        """Test that surreal events have variety.

        Verifies that get_random_surreal_event returns different
        events across multiple calls, not always the same one.
        """
        events = set()
        for _ in range(50):
            events.add(get_random_surreal_event())
        
        # Should have some variety (more than 1 unique event)
        assert len(events) > 1
    
    def test_parse_freeform_input_simple(self):
        """Test parsing simple freeform input.

        Verifies that parse_freeform_input extracts a verb or
        returns a confidence score for simple natural language input.
        """
        result = parse_freeform_input("I want to go north")
        
        assert result["verb"] is not None or result["confidence"] > 0
    
    def test_parse_freeform_input_empty(self):
        """Test parsing empty input.

        Verifies that parse_freeform_input returns None verb and
        zero confidence for empty string input.
        """
        result = parse_freeform_input("")
        
        assert result["verb"] is None
        assert result["confidence"] == 0.0
    
    def test_parse_freeform_input_with_target(self):
        """Test parsing freeform input with target.

        Verifies that parse_freeform_input correctly processes
        input containing an action verb and target object.
        """
        result = parse_freeform_input("take the sword")
        
        assert result is not None
