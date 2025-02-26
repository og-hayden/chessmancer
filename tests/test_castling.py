import unittest
import pygame
import sys
from chess_board import ChessBoard, ChessPiece, KING, ROOK, QUEEN, BISHOP, KNIGHT, PAWN, MODE_HUMAN_VS_HUMAN

class TestCastling(unittest.TestCase):
    """Test cases for castling functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        # Initialize pygame
        pygame.init()
        
        # Create a board with no AI
        self.board = ChessBoard(game_mode=MODE_HUMAN_VS_HUMAN)
        
        # Clear the board for custom setup
        self.board.board = [[None for _ in range(8)] for _ in range(8)]
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_kingside_castling_white(self):
        """Test kingside castling for white."""
        # Set up the board with just a king and rook in their initial positions
        self.board.board[7][4] = ChessPiece(KING, 'white', (7, 4))
        self.board.board[7][7] = ChessPiece(ROOK, 'white', (7, 7))
        
        # Select the king
        self.board.select_piece(7, 4)
        
        # Verify castling is a legal move
        self.assertIn((7, 6), self.board.legal_moves)
        
        # Perform the castling move
        self.board.move_piece(7, 6)
        
        # Verify the king moved
        self.assertIsNotNone(self.board.board[7][6])
        self.assertEqual(self.board.board[7][6].piece_type, KING)
        
        # Verify the rook moved
        self.assertIsNotNone(self.board.board[7][5])
        self.assertEqual(self.board.board[7][5].piece_type, ROOK)
        
        # Verify the original positions are empty
        self.assertIsNone(self.board.board[7][4])
        self.assertIsNone(self.board.board[7][7])
    
    def test_queenside_castling_white(self):
        """Test queenside castling for white."""
        # Set up the board with just a king and rook in their initial positions
        self.board.board[7][4] = ChessPiece(KING, 'white', (7, 4))
        self.board.board[7][0] = ChessPiece(ROOK, 'white', (7, 0))
        
        # Select the king
        self.board.select_piece(7, 4)
        
        # Verify castling is a legal move
        self.assertIn((7, 2), self.board.legal_moves)
        
        # Perform the castling move
        self.board.move_piece(7, 2)
        
        # Verify the king moved
        self.assertIsNotNone(self.board.board[7][2])
        self.assertEqual(self.board.board[7][2].piece_type, KING)
        
        # Verify the rook moved
        self.assertIsNotNone(self.board.board[7][3])
        self.assertEqual(self.board.board[7][3].piece_type, ROOK)
        
        # Verify the original positions are empty
        self.assertIsNone(self.board.board[7][4])
        self.assertIsNone(self.board.board[7][0])
    
    def test_kingside_castling_black(self):
        """Test kingside castling for black."""
        # Set up the board with just a king and rook in their initial positions
        self.board.board[0][4] = ChessPiece(KING, 'black', (0, 4))
        self.board.board[0][7] = ChessPiece(ROOK, 'black', (0, 7))
        
        # Set turn to black
        self.board.turn = 'black'
        
        # Select the king
        self.board.select_piece(0, 4)
        
        # Verify castling is a legal move
        self.assertIn((0, 6), self.board.legal_moves)
        
        # Perform the castling move
        self.board.move_piece(0, 6)
        
        # Verify the king moved
        self.assertIsNotNone(self.board.board[0][6])
        self.assertEqual(self.board.board[0][6].piece_type, KING)
        
        # Verify the rook moved
        self.assertIsNotNone(self.board.board[0][5])
        self.assertEqual(self.board.board[0][5].piece_type, ROOK)
        
        # Verify the original positions are empty
        self.assertIsNone(self.board.board[0][4])
        self.assertIsNone(self.board.board[0][7])
    
    def test_queenside_castling_black(self):
        """Test queenside castling for black."""
        # Set up the board with just a king and rook in their initial positions
        self.board.board[0][4] = ChessPiece(KING, 'black', (0, 4))
        self.board.board[0][0] = ChessPiece(ROOK, 'black', (0, 0))
        
        # Set turn to black
        self.board.turn = 'black'
        
        # Select the king
        self.board.select_piece(0, 4)
        
        # Verify castling is a legal move
        self.assertIn((0, 2), self.board.legal_moves)
        
        # Perform the castling move
        self.board.move_piece(0, 2)
        
        # Verify the king moved
        self.assertIsNotNone(self.board.board[0][2])
        self.assertEqual(self.board.board[0][2].piece_type, KING)
        
        # Verify the rook moved
        self.assertIsNotNone(self.board.board[0][3])
        self.assertEqual(self.board.board[0][3].piece_type, ROOK)
        
        # Verify the original positions are empty
        self.assertIsNone(self.board.board[0][4])
        self.assertIsNone(self.board.board[0][0])
    
    def test_castling_blocked(self):
        """Test that castling is not allowed when pieces are in the way."""
        # Set up the board with a king, rook, and a blocking piece
        self.board.board[7][4] = ChessPiece(KING, 'white', (7, 4))
        self.board.board[7][7] = ChessPiece(ROOK, 'white', (7, 7))
        self.board.board[7][5] = ChessPiece(ROOK, 'white', (7, 5))  # Blocking piece
        
        # Select the king
        self.board.select_piece(7, 4)
        
        # Verify castling is not a legal move
        self.assertNotIn((7, 6), self.board.legal_moves)
    
    def test_castling_after_king_moved(self):
        """Test that castling is not allowed after the king has moved."""
        # Set up the board with a king and rook
        king = ChessPiece(KING, 'white', (7, 4))
        king.has_moved = True  # King has already moved
        self.board.board[7][4] = king
        self.board.board[7][7] = ChessPiece(ROOK, 'white', (7, 7))
        
        # Select the king
        self.board.select_piece(7, 4)
        
        # Verify castling is not a legal move
        self.assertNotIn((7, 6), self.board.legal_moves)
    
    def test_castling_after_rook_moved(self):
        """Test that castling is not allowed after the rook has moved."""
        # Set up the board with a king and rook
        self.board.board[7][4] = ChessPiece(KING, 'white', (7, 4))
        rook = ChessPiece(ROOK, 'white', (7, 7))
        rook.has_moved = True  # Rook has already moved
        self.board.board[7][7] = rook
        
        # Select the king
        self.board.select_piece(7, 4)
        
        # Verify castling is not a legal move
        self.assertNotIn((7, 6), self.board.legal_moves)
    
    def test_castling_king_in_check(self):
        """Test that castling is not allowed when the king is in check."""
        # Set up the board with a king, rook, and an enemy queen checking the king
        self.board.board[7][4] = ChessPiece(KING, 'white', (7, 4))
        self.board.board[7][7] = ChessPiece(ROOK, 'white', (7, 7))
        self.board.board[4][4] = ChessPiece(QUEEN, 'black', (4, 4))  # Queen checking the king
        
        # Select the king
        self.board.select_piece(7, 4)
        
        # Verify castling is not a legal move
        self.assertNotIn((7, 6), self.board.legal_moves)
    
    def test_castling_through_check(self):
        """Test that castling is not allowed when the king would pass through a square that is under attack."""
        # Set up the board with a king, rook, and an enemy rook attacking the square the king would pass through
        self.board.board[7][4] = ChessPiece(KING, 'white', (7, 4))
        self.board.board[7][7] = ChessPiece(ROOK, 'white', (7, 7))
        self.board.board[5][5] = ChessPiece(ROOK, 'black', (5, 5))  # Rook attacking f1 (7,5)
        
        # Select the king
        self.board.select_piece(7, 4)
        
        # Verify castling is not a legal move
        self.assertNotIn((7, 6), self.board.legal_moves)
    
    def test_castling_into_check(self):
        """Test that castling is not allowed when the king would end up in check."""
        # Set up the board with a king, rook, and an enemy bishop attacking the square where the king would end up
        self.board.board[7][4] = ChessPiece(KING, 'white', (7, 4))
        self.board.board[7][7] = ChessPiece(ROOK, 'white', (7, 7))
        self.board.board[5][4] = ChessPiece(BISHOP, 'black', (5, 4))  # Bishop attacking g1 (7,6)
        
        # Select the king
        self.board.select_piece(7, 4)
        
        # Verify castling is not a legal move
        self.assertNotIn((7, 6), self.board.legal_moves)

if __name__ == '__main__':
    unittest.main() 