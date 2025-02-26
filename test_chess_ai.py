import unittest
import os
import platform
from chess_ai import ChessAI

class TestChessAI(unittest.TestCase):
    """Test cases for the ChessAI class."""
    
    def setUp(self):
        """Set up a new ChessAI instance for each test."""
        # Use a lower difficulty and time limit for faster tests
        self.ai = ChessAI(difficulty=5, time_limit=0.05)
    
    def tearDown(self):
        """Clean up after each test."""
        if self.ai:
            self.ai.close()
    
    def test_init(self):
        """Test initialization of the AI."""
        self.assertIsNotNone(self.ai.board)
        self.assertEqual(self.ai.difficulty, 5)
        self.assertEqual(self.ai.time_limit, 0.05)
    
    def test_find_stockfish(self):
        """Test finding Stockfish executable."""
        # This test just verifies the method runs without errors
        # The actual result depends on whether Stockfish is installed
        result = self.ai._find_stockfish()
        # If Stockfish is found, result should be a string path
        # If not found, result should be None
        if result is not None:
            self.assertIsInstance(result, str)
            self.assertTrue(os.path.exists(result))
    
    def test_get_best_move_initial_position(self):
        """Test getting a move from the initial position."""
        # The board is in the initial position, so there should be a valid move
        move = self.ai.get_best_move()
        
        # If Stockfish is available, we should get a valid move
        if self.ai.engine:
            self.assertIsNotNone(move)
            self.assertEqual(len(move), 2)  # Should be ((from_row, from_col), (to_row, to_col))
            
            # Check that the move is from a valid position
            from_pos, to_pos = move
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            # In the initial position, pieces can move from rows 0, 1 (black) or 6, 7 (white)
            # The AI might be playing as either color
            self.assertIn(from_row, [0, 1, 6, 7])
            self.assertGreaterEqual(from_col, 0)
            self.assertLess(from_col, 8)
            
            # The destination should be on the board
            self.assertGreaterEqual(to_row, 0)
            self.assertLess(to_row, 8)
            self.assertGreaterEqual(to_col, 0)
            self.assertLess(to_col, 8)
    
    def test_update_board(self):
        """Test updating the board with moves."""
        # Make a simple move: e2-e4 (white pawn)
        moves = [((6, 4), (4, 4))]
        self.ai.update_board(moves)
        
        # The board should reflect this move
        # In python-chess, e2 is square 12 (file 4, rank 1) and e4 is square 28 (file 4, rank 3)
        # But our coordinates are flipped, so we need to check differently
        
        # After e2-e4, it should be black's turn
        self.assertEqual(self.ai.board.turn, False)  # False is black in python-chess
        
        # Make another move: e7-e5 (black pawn)
        moves.append(((1, 4), (3, 4)))
        self.ai.update_board(moves)
        
        # Now it should be white's turn again
        self.assertEqual(self.ai.board.turn, True)  # True is white in python-chess
    
    def test_game_over_detection(self):
        """Test detection of game over conditions."""
        # Initial position is not game over
        self.assertFalse(self.ai.is_game_over())
        self.assertEqual(self.ai.get_game_result(), "Game in progress")
        
        # Set up a checkmate position (fool's mate)
        # 1. f2-f3, e7-e5
        # 2. g2-g4, Qd8-h4#
        moves = [
            ((6, 5), (5, 5)),  # f2-f3
            ((1, 4), (3, 4)),  # e7-e5
            ((6, 6), (4, 6)),  # g2-g4
            ((0, 3), (4, 7))   # Qd8-h4#
        ]
        self.ai.update_board(moves)
        
        # Now the game should be over
        self.assertTrue(self.ai.is_game_over())
        self.assertEqual(self.ai.get_game_result(), "Checkmate")

if __name__ == '__main__':
    unittest.main() 