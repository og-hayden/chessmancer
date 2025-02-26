import unittest
import pygame
import sys
from chess_board import ChessBoard, ChessPiece, PAWN, MODE_HUMAN_VS_HUMAN

class TestEnPassant(unittest.TestCase):
    """Test cases for en passant functionality."""
    
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
    
    def test_en_passant_white_captures_left(self):
        """Test en passant capture by white pawn to the left."""
        # Set up the board with a white pawn and a black pawn
        white_pawn = ChessPiece(PAWN, 'white', (3, 4))
        self.board.board[3][4] = white_pawn
        
        black_pawn = ChessPiece(PAWN, 'black', (1, 3))
        self.board.board[1][3] = black_pawn
        
        # Move the black pawn two squares forward (simulating the previous move)
        self.board.board[3][3] = black_pawn
        self.board.board[1][3] = None
        black_pawn.position = (3, 3)
        self.board.last_pawn_double_move = (3, 3)
        
        # Set turn to white
        self.board.turn = 'white'
        
        # Select the white pawn
        self.board.select_piece(3, 4)
        
        # Verify en passant is a legal move
        self.assertIn((2, 3), self.board.legal_moves)
        
        # Perform the en passant capture
        self.board.move_piece(2, 3)
        
        # Verify the white pawn moved
        self.assertIsNotNone(self.board.board[2][3])
        self.assertEqual(self.board.board[2][3].piece_type, PAWN)
        self.assertEqual(self.board.board[2][3].color, 'white')
        
        # Verify the black pawn was captured
        self.assertIsNone(self.board.board[3][3])
        
        # Verify the original position is empty
        self.assertIsNone(self.board.board[3][4])
    
    def test_en_passant_white_captures_right(self):
        """Test en passant capture by white pawn to the right."""
        # Set up the board with a white pawn and a black pawn
        white_pawn = ChessPiece(PAWN, 'white', (3, 4))
        self.board.board[3][4] = white_pawn
        
        black_pawn = ChessPiece(PAWN, 'black', (1, 5))
        self.board.board[1][5] = black_pawn
        
        # Move the black pawn two squares forward (simulating the previous move)
        self.board.board[3][5] = black_pawn
        self.board.board[1][5] = None
        black_pawn.position = (3, 5)
        self.board.last_pawn_double_move = (3, 5)
        
        # Set turn to white
        self.board.turn = 'white'
        
        # Select the white pawn
        self.board.select_piece(3, 4)
        
        # Verify en passant is a legal move
        self.assertIn((2, 5), self.board.legal_moves)
        
        # Perform the en passant capture
        self.board.move_piece(2, 5)
        
        # Verify the white pawn moved
        self.assertIsNotNone(self.board.board[2][5])
        self.assertEqual(self.board.board[2][5].piece_type, PAWN)
        self.assertEqual(self.board.board[2][5].color, 'white')
        
        # Verify the black pawn was captured
        self.assertIsNone(self.board.board[3][5])
        
        # Verify the original position is empty
        self.assertIsNone(self.board.board[3][4])
    
    def test_en_passant_black_captures_left(self):
        """Test en passant capture by black pawn to the left."""
        # Set up the board with a black pawn and a white pawn
        black_pawn = ChessPiece(PAWN, 'black', (4, 4))
        self.board.board[4][4] = black_pawn
        
        white_pawn = ChessPiece(PAWN, 'white', (6, 3))
        self.board.board[6][3] = white_pawn
        
        # Move the white pawn two squares forward (simulating the previous move)
        self.board.board[4][3] = white_pawn
        self.board.board[6][3] = None
        white_pawn.position = (4, 3)
        self.board.last_pawn_double_move = (4, 3)
        
        # Set turn to black
        self.board.turn = 'black'
        
        # Select the black pawn
        self.board.select_piece(4, 4)
        
        # Verify en passant is a legal move
        self.assertIn((5, 3), self.board.legal_moves)
        
        # Perform the en passant capture
        self.board.move_piece(5, 3)
        
        # Verify the black pawn moved
        self.assertIsNotNone(self.board.board[5][3])
        self.assertEqual(self.board.board[5][3].piece_type, PAWN)
        self.assertEqual(self.board.board[5][3].color, 'black')
        
        # Verify the white pawn was captured
        self.assertIsNone(self.board.board[4][3])
        
        # Verify the original position is empty
        self.assertIsNone(self.board.board[4][4])
    
    def test_en_passant_black_captures_right(self):
        """Test en passant capture by black pawn to the right."""
        # Set up the board with a black pawn and a white pawn
        black_pawn = ChessPiece(PAWN, 'black', (4, 4))
        self.board.board[4][4] = black_pawn
        
        white_pawn = ChessPiece(PAWN, 'white', (6, 5))
        self.board.board[6][5] = white_pawn
        
        # Move the white pawn two squares forward (simulating the previous move)
        self.board.board[4][5] = white_pawn
        self.board.board[6][5] = None
        white_pawn.position = (4, 5)
        self.board.last_pawn_double_move = (4, 5)
        
        # Set turn to black
        self.board.turn = 'black'
        
        # Select the black pawn
        self.board.select_piece(4, 4)
        
        # Verify en passant is a legal move
        self.assertIn((5, 5), self.board.legal_moves)
        
        # Perform the en passant capture
        self.board.move_piece(5, 5)
        
        # Verify the black pawn moved
        self.assertIsNotNone(self.board.board[5][5])
        self.assertEqual(self.board.board[5][5].piece_type, PAWN)
        self.assertEqual(self.board.board[5][5].color, 'black')
        
        # Verify the white pawn was captured
        self.assertIsNone(self.board.board[4][5])
        
        # Verify the original position is empty
        self.assertIsNone(self.board.board[4][4])
    
    def test_en_passant_only_available_immediately(self):
        """Test that en passant is only available immediately after the pawn's double move."""
        # Set up the board with a white pawn and a black pawn
        white_pawn = ChessPiece(PAWN, 'white', (3, 4))
        self.board.board[3][4] = white_pawn
        
        black_pawn = ChessPiece(PAWN, 'black', (1, 5))
        self.board.board[1][5] = black_pawn
        
        # Move the black pawn two squares forward (simulating the previous move)
        self.board.board[3][5] = black_pawn
        self.board.board[1][5] = None
        black_pawn.position = (3, 5)
        self.board.last_pawn_double_move = (3, 5)
        
        # Set turn to white
        self.board.turn = 'white'
        
        # Select the white pawn
        self.board.select_piece(3, 4)
        
        # Verify en passant is a legal move
        self.assertIn((2, 5), self.board.legal_moves)
        
        # Simulate a different move being made
        self.board.last_pawn_double_move = None
        
        # Select the white pawn again
        self.board.select_piece(3, 4)
        
        # Verify en passant is no longer a legal move
        self.assertNotIn((2, 5), self.board.legal_moves)

if __name__ == '__main__':
    unittest.main() 