"""
Chess Bot with Minimax, Alpha-Beta Pruning, and Dynamic Programming
Main script to run the chess game with starting window
"""
import os
import sys

# Make sure we're in the correct directory
chess_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(chess_dir)

# Import essential modules first
try:
    import pygame
    import chess
except ImportError as e:
    print(f"Missing core package: {e}")
    print("Please install the required packages using:")
    print("pip install pygame python-chess")
    sys.exit(1)

# Import the updated pygame interface with starting window
import Chess_pygame

if __name__ == "__main__":
    Chess_pygame.main()