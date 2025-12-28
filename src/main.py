"""
Main Module - Entry point and main game loop for Infinite Story Loop.

This module contains the main game loop and console interface for the
Infinite Story Loop text adventure. It handles user interaction,
display formatting, and coordinates the story engine components.
"""

from __future__ import annotations
import sys
import os
from typing import Optional

from .story_loop import InfiniteStoryLoop
from .player import Player
from .utils import (
    StateManager,
    GameLogger,
    create_separator,
    create_header,
)


class ConsoleInterface:
    """
    Handles console display and user interaction.
    
    Provides methods for displaying story text, choices, and
    handling user input in a clean, readable format.
    
    Attributes:
        width: Console display width
        separator_char: Character for separators
    """
    
    def __init__(self, width: int = 70):
        """
        Initialize the console interface.
        
        Args:
            width: Display width for text formatting
        """
        self.width = width
        self.separator_char = "═"
    
    def clear_screen(self) -> None:
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_title(self) -> None:
        """Display the game title screen."""
        title = r"""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║     ██╗███╗   ██╗███████╗██╗███╗   ██╗██╗████████╗███████╗            ║
    ║     ██║████╗  ██║██╔════╝██║████╗  ██║██║╚══██╔══╝██╔════╝            ║
    ║     ██║██╔██╗ ██║█████╗  ██║██╔██╗ ██║██║   ██║   █████╗              ║
    ║     ██║██║╚██╗██║██╔══╝  ██║██║╚██╗██║██║   ██║   ██╔══╝              ║
    ║     ██║██║ ╚████║██║     ██║██║ ╚████║██║   ██║   ███████╗            ║
    ║     ╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚══════╝            ║
    ║                                                                       ║
    ║         ███████╗████████╗ ██████╗ ██████╗ ██╗   ██╗                   ║
    ║         ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝                   ║
    ║         ███████╗   ██║   ██║   ██║██████╔╝ ╚████╔╝                    ║
    ║         ╚════██║   ██║   ██║   ██║██╔══██╗  ╚██╔╝                     ║
    ║         ███████║   ██║   ╚██████╔╝██║  ██║   ██║                      ║
    ║         ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝                      ║
    ║                                                                       ║
    ║                    ██╗      ██████╗  ██████╗ ██████╗                  ║
    ║                    ██║     ██╔═══██╗██╔═══██╗██╔══██╗                 ║
    ║                    ██║     ██║   ██║██║   ██║██████╔╝                 ║
    ║                    ██║     ██║   ██║██║   ██║██╔═══╝                  ║
    ║                    ███████╗╚██████╔╝╚██████╔╝██║                      ║
    ║                    ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝                      ║
    ║                                                                       ║
    ║                  A Surreal Text Adventure                             ║
    ║             Where Paradoxes Reshape Reality                           ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
"""
        print(title)
    
    def display_separator(self, char: Optional[str] = None) -> None:
        """Display a separator line."""
        char = char or self.separator_char
        print(create_separator(char, self.width))
    
    def display_text(self, text: str, prefix: str = "") -> None:
        """
        Display formatted text.
        
        Args:
            text: Text to display
            prefix: Optional prefix for each line
        """
        if prefix:
            lines = text.split('\n')
            for line in lines:
                print(f"{prefix}{line}")
        else:
            print(text)
        print()
    
    def display_choices(self, choices: list[str]) -> None:
        """
        Display available choices.
        
        Args:
            choices: List of choice texts
        """
        if not choices:
            return
        
        print("What do you do?")
        print()
        for i, choice in enumerate(choices, 1):
            print(f"  [{i}] {choice}")
        print()
    
    def display_paradox_warning(self, paradox_type: str, severity: int) -> None:
        """
        Display a paradox detection warning.
        
        Args:
            paradox_type: Type of paradox detected
            severity: Severity level (1-10)
        """
        severity_bar = "█" * severity + "░" * (10 - severity)
        print()
        print("╔════════════════════════════════════════╗")
        print("║        ⚠ PARADOX DETECTED ⚠           ║")
        print("╠════════════════════════════════════════╣")
        print(f"║  Type: {paradox_type:<30}║")
        print(f"║  Severity: [{severity_bar}]     ║")
        print("║  Reality is being rewritten...        ║")
        print("╚════════════════════════════════════════╝")
        print()
    
    def get_input(self, prompt: str = "> ") -> str:
        """
        Get input from the user.
        
        Args:
            prompt: Input prompt to display
            
        Returns:
            User input string
        """
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return "quit"
    
    def display_error(self, message: str) -> None:
        """Display an error message."""
        print(f"\n⚠ {message}\n")
    
    def display_save_message(self, path: str) -> None:
        """Display save confirmation."""
        print(f"\n✓ Game saved to: {path}\n")
    
    def display_load_message(self, success: bool) -> None:
        """Display load result."""
        if success:
            print("\n✓ Game loaded successfully!\n")
        else:
            print("\n⚠ Failed to load game.\n")


class GameController:
    """
    Main game controller that coordinates all components.
    
    Manages the game loop, handles saving/loading, and
    coordinates between the story engine and console interface.
    
    Attributes:
        game: The InfiniteStoryLoop game engine
        interface: Console interface for display
        state_manager: Handles save/load operations
        logger: Game event logger
        running: Whether the game is currently running
    """
    
    def __init__(self):
        """Initialize the game controller."""
        self.logger = GameLogger(console_output=False)
        self.game = InfiniteStoryLoop(logger=self.logger)
        self.interface = ConsoleInterface()
        self.state_manager = StateManager()
        self.running = False
    
    def start(self) -> None:
        """Start the game."""
        self.running = True
        self.interface.clear_screen()
        self.interface.display_title()
        
        print("\nPress ENTER to begin your journey...")
        print("Type 'help' at any time for commands.\n")
        self.interface.get_input()
        
        self._show_current_scene()
        self._game_loop()
    
    def _game_loop(self) -> None:
        """Main game loop."""
        while self.running:
            # Get player input
            user_input = self.interface.get_input()
            
            if not user_input:
                continue
            
            # Process input through the story engine
            response = self.game.process_input(user_input)
            
            # Handle different response types
            self._handle_response(response)
    
    def _handle_response(self, response: dict) -> None:
        """
        Handle a response from the story engine.
        
        Args:
            response: Response dictionary from the engine
        """
        response_type = response.get("type", "story")
        
        if response_type == "quit":
            self._quit_game(response.get("text", ""))
            return
        
        if response_type == "save":
            self._save_game()
            return
        
        if response_type == "load":
            self._load_game()
            return
        
        if response_type == "paradox":
            self.interface.display_paradox_warning(
                response.get("paradox_type", "UNKNOWN"),
                response.get("severity", 5)
            )
        
        # Display the response text
        self.interface.display_separator("─")
        self.interface.display_text(response.get("text", ""))
        
        # Display choices if any
        choices = response.get("choices", [])
        if choices:
            self.interface.display_choices(choices)
        
        # Auto-save periodically
        self.state_manager.auto_save(self.game.to_dict())
    
    def _show_current_scene(self) -> None:
        """Display the current scene."""
        self.interface.display_separator()
        self.interface.display_text(self.game.get_current_text())
        
        choices = self.game.get_current_choices()
        if choices:
            self.interface.display_choices(choices)
    
    def _save_game(self) -> None:
        """Save the current game state."""
        try:
            path = self.state_manager.save(
                self.game.to_dict(),
                "manual_save"
            )
            self.interface.display_save_message(path)
        except Exception as e:
            self.interface.display_error(f"Failed to save: {e}")
    
    def _load_game(self) -> None:
        """Load a saved game state."""
        saves = self.state_manager.list_saves()
        
        if not saves:
            self.interface.display_error("No save files found.")
            return
        
        print("\nAvailable saves:")
        for i, save in enumerate(saves, 1):
            print(f"  [{i}] {save['filename']} ({save['timestamp']})")
        print()
        
        choice = self.interface.get_input("Enter save number (or 'cancel'): ")
        
        if choice.lower() == 'cancel':
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(saves):
                game_state = self.state_manager.load(saves[index]['filename'])
                if game_state:
                    self.game = InfiniteStoryLoop.from_dict(game_state)
                    self.interface.display_load_message(True)
                    self._show_current_scene()
                else:
                    self.interface.display_load_message(False)
            else:
                self.interface.display_error("Invalid selection.")
        except ValueError:
            self.interface.display_error("Invalid input.")
    
    def _quit_game(self, message: str = "") -> None:
        """
        Quit the game.
        
        Args:
            message: Optional farewell message
        """
        self.running = False
        print()
        self.interface.display_separator()
        print(message or "The story closes, but it never truly ends...")
        self.interface.display_separator()
        print("\nThank you for playing Infinite Story Loop!")
        print()


def main() -> int:
    """
    Main entry point for the game.
    
    Returns:
        Exit code (0 for success)
    """
    try:
        controller = GameController()
        controller.start()
        return 0
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("The story has encountered an unexpected paradox...")
        return 1


if __name__ == "__main__":
    sys.exit(main())
