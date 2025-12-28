#!/usr/bin/env python3
"""
Infinite Story Loop - Application Entry Point

A surreal text adventure that dynamically detects narrative loops
and paradoxes in the player's choices. When a contradiction or loop
occurs, the story rewrites itself in real-time to reconcile the
paradox, producing unpredictable, mind-bending outcomes.

Usage:
    python run.py
"""

import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main


if __name__ == "__main__":
    sys.exit(main())
