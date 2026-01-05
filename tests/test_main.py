"""
Unit tests for the Main module.

Tests the ConsoleInterface and GameController classes.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.main import ConsoleInterface, GameController


class TestConsoleInterface:
    """Tests for the ConsoleInterface class."""
    
    def test_interface_creation(self):
        """Test creating a console interface.

        Verifies that a ConsoleInterface is created with default width
        and separator character.
        """
        interface = ConsoleInterface()
        
        assert interface.width == 70
        assert interface.separator_char == "═"
    
    def test_interface_custom_width(self):
        """Test creating interface with custom width.

        Verifies that the interface width can be customized during creation.
        """
        interface = ConsoleInterface(width=80)
        
        assert interface.width == 80
    
    def test_display_separator(self, capsys):
        """Test displaying a separator.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        interface = ConsoleInterface(width=10)
        
        interface.display_separator("=")
        
        captured = capsys.readouterr()
        assert "==========" in captured.out
    
    def test_display_text(self, capsys):
        """Test displaying text.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        interface = ConsoleInterface()
        
        interface.display_text("Hello, World!")
        
        captured = capsys.readouterr()
        assert "Hello, World!" in captured.out
    
    def test_display_text_with_prefix(self, capsys):
        """Test displaying text with prefix.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        interface = ConsoleInterface()
        
        interface.display_text("Test line", prefix=">> ")
        
        captured = capsys.readouterr()
        assert ">> Test line" in captured.out
    
    def test_display_choices(self, capsys):
        """Test displaying choices.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        interface = ConsoleInterface()
        
        interface.display_choices(["Go north", "Go south", "Look around"])
        
        captured = capsys.readouterr()
        assert "[1] Go north" in captured.out
        assert "[2] Go south" in captured.out
        assert "[3] Look around" in captured.out
    
    def test_display_choices_empty(self, capsys):
        """Test displaying empty choices.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        interface = ConsoleInterface()
        
        interface.display_choices([])
        
        captured = capsys.readouterr()
        assert captured.out == ""
    
    def test_display_paradox_warning(self, capsys):
        """Test displaying paradox warning.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        interface = ConsoleInterface()
        
        interface.display_paradox_warning("TEMPORAL_LOOP", 7)
        
        captured = capsys.readouterr()
        assert "PARADOX DETECTED" in captured.out
        assert "TEMPORAL_LOOP" in captured.out
    
    def test_display_error(self, capsys):
        """Test displaying an error.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        interface = ConsoleInterface()
        
        interface.display_error("Something went wrong")
        
        captured = capsys.readouterr()
        assert "Something went wrong" in captured.out
        assert "⚠" in captured.out
    
    def test_display_save_message(self, capsys):
        """Test displaying save message.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        interface = ConsoleInterface()
        
        interface.display_save_message("/path/to/save.json")
        
        captured = capsys.readouterr()
        assert "saved" in captured.out.lower()
        assert "/path/to/save.json" in captured.out
    
    def test_display_load_message_success(self, capsys):
        """Test displaying load success message.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        interface = ConsoleInterface()
        
        interface.display_load_message(True)
        
        captured = capsys.readouterr()
        assert "successfully" in captured.out.lower()
    
    def test_display_load_message_failure(self, capsys):
        """Test displaying load failure message.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        interface = ConsoleInterface()
        
        interface.display_load_message(False)
        
        captured = capsys.readouterr()
        assert "failed" in captured.out.lower()
    
    def test_get_input(self):
        """Test getting input from user.

        Verifies that user input is correctly returned.
        """
        interface = ConsoleInterface()
        
        with patch('builtins.input', return_value="test input"):
            result = interface.get_input()
        
        assert result == "test input"
    
    def test_get_input_strips_whitespace(self):
        """Test that input is stripped.

        Verifies that leading and trailing whitespace is removed from input.
        """
        interface = ConsoleInterface()
        
        with patch('builtins.input', return_value="  test  "):
            result = interface.get_input()
        
        assert result == "test"
    
    def test_get_input_eof(self):
        """Test handling EOF.

        Verifies that EOFError is handled gracefully by returning 'quit'.
        """
        interface = ConsoleInterface()
        
        with patch('builtins.input', side_effect=EOFError):
            result = interface.get_input()
        
        assert result == "quit"
    
    def test_get_input_keyboard_interrupt(self):
        """Test handling keyboard interrupt.

        Verifies that KeyboardInterrupt is handled gracefully by returning 'quit'.
        """
        interface = ConsoleInterface()
        
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            result = interface.get_input()
        
        assert result == "quit"


class TestGameController:
    """Tests for the GameController class."""
    
    def test_controller_creation(self):
        """Test creating a game controller.

        Verifies that a GameController is created with all required components.
        """
        controller = GameController()
        
        assert controller.game is not None
        assert controller.interface is not None
        assert controller.state_manager is not None
        assert controller.running is False
    
    def test_handle_response_story(self):
        """Test handling story response.

        Verifies that story-type responses are processed without errors.
        """
        controller = GameController()
        
        response = {
            "type": "story",
            "text": "You enter a dark room.",
            "choices": ["Go north", "Look around"],
        }
        
        # Should not raise an exception
        controller._handle_response(response)
    
    def test_handle_response_paradox(self):
        """Test handling paradox response.

        Verifies that paradox-type responses are processed without errors.
        """
        controller = GameController()
        
        response = {
            "type": "paradox",
            "text": "Reality shifts...",
            "choices": [],
            "paradox_type": "TEMPORAL_LOOP",
            "severity": 5,
        }
        
        # Should not raise an exception
        controller._handle_response(response)
    
    def test_handle_response_system(self):
        """Test handling system response.

        Verifies that system-type responses are processed without errors.
        """
        controller = GameController()
        
        response = {
            "type": "system",
            "text": "Help text here",
            "choices": [],
        }
        
        # Should not raise an exception
        controller._handle_response(response)
    
    def test_handle_response_quit(self):
        """Test handling quit response.

        Verifies that quit-type responses stop the game controller.
        """
        controller = GameController()
        controller.running = True
        
        response = {
            "type": "quit",
            "text": "Goodbye!",
            "choices": [],
        }
        
        controller._handle_response(response)
        
        assert controller.running is False
    
    def test_show_current_scene(self, capsys):
        """Test showing current scene.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        controller = GameController()
        
        controller._show_current_scene()
        
        captured = capsys.readouterr()
        assert len(captured.out) > 0
    
    def test_quit_game(self, capsys):
        """Test quitting the game.

        Args:
            capsys: Pytest fixture to capture stdout/stderr.
        """
        controller = GameController()
        controller.running = True
        
        controller._quit_game("Farewell!")
        
        assert controller.running is False
        captured = capsys.readouterr()
        assert "Thank you" in captured.out


class TestMainFunction:
    """Tests for the main function."""
    
    def test_main_returns_int(self):
        """Test that main returns an integer.

        Verifies that the main function returns an integer exit code.
        """
        from src.main import main
        
        # Mock the controller to quit immediately
        with patch.object(GameController, 'start', side_effect=Exception("Test exit")):
            result = main()
        
        assert isinstance(result, int)
    
    def test_main_handles_exception(self):
        """Test that main handles exceptions gracefully.

        Verifies that exceptions during initialization return exit code 1.
        """
        from src.main import main
        
        with patch.object(GameController, '__init__', side_effect=Exception("Init failed")):
            result = main()
        
        assert result == 1
