# Chessmancer

A chess board implementation using Pygame with an AI opponent powered by the Stockfish chess engine.

## Setup

1. Install the required dependencies:
```
pip install -r requirements.txt
```

2. Run the game:
```
python chess_board.py
```

## Features

- Visual chess board with standard piece placement
- Piece movement with drag and drop
- Highlights legal moves
- GPU acceleration enabled for systems with compatible hardware
- AI opponent powered by Stockfish chess engine
- Multiple difficulty levels for the AI
- Game mode selection (Human vs Human or Human vs AI)

## Controls

- Click and drag pieces to move them
- Click buttons on the right panel to change game modes
- ESC to quit the game

## AI Opponent

The AI opponent uses the Stockfish chess engine, one of the strongest open-source chess engines available. The game will automatically download Stockfish if it's not found on your system.

You can select from three difficulty levels:
- Easy: Suitable for beginners
- Medium: Challenging for casual players
- Hard: Strong play for experienced chess players

## Requirements

- Python 3.6+
- Pygame
- python-chess
- Stockfish chess engine (automatically downloaded if not found) 