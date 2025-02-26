import unittest
from chess_board import ChessPiece, ChessBoard, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, create_piece_images

class TestChessPiece(unittest.TestCase):
    """Test cases for the ChessPiece class."""
    
    def test_init(self):
        """Test initialization of a chess piece."""
        piece = ChessPiece(PAWN, 'white', (6, 0))
        self.assertEqual(piece.piece_type, PAWN)
        self.assertEqual(piece.color, 'white')
        self.assertEqual(piece.position, (6, 0))
        self.assertFalse(piece.has_moved)
    
    def test_get_image_key(self):
        """Test getting the image key for a piece."""
        piece = ChessPiece(KNIGHT, 'black', (0, 1))
        self.assertEqual(piece.get_image_key(), 'black_knight')
        
    def test_create_piece_images(self):
        """Test that piece images are created correctly."""
        piece_images = create_piece_images()
        self.assertIn('white_pawn', piece_images)
        self.assertIn('black_king', piece_images)
        self.assertEqual(len(piece_images), 12)  # 6 piece types * 2 colors

class TestChessBoard(unittest.TestCase):
    """Test cases for the ChessBoard class."""
    
    def setUp(self):
        """Set up a new chess board for each test."""
        self.board = ChessBoard()
    
    def test_initial_setup(self):
        """Test that the board is set up correctly."""
        # Check pawns
        for col in range(8):
            self.assertIsNotNone(self.board.board[1][col])
            self.assertEqual(self.board.board[1][col].piece_type, PAWN)
            self.assertEqual(self.board.board[1][col].color, 'black')
            
            self.assertIsNotNone(self.board.board[6][col])
            self.assertEqual(self.board.board[6][col].piece_type, PAWN)
            self.assertEqual(self.board.board[6][col].color, 'white')
        
        # Check back row pieces
        back_row_pieces = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
        for col, piece_type in enumerate(back_row_pieces):
            self.assertIsNotNone(self.board.board[0][col])
            self.assertEqual(self.board.board[0][col].piece_type, piece_type)
            self.assertEqual(self.board.board[0][col].color, 'black')
            
            self.assertIsNotNone(self.board.board[7][col])
            self.assertEqual(self.board.board[7][col].piece_type, piece_type)
            self.assertEqual(self.board.board[7][col].color, 'white')
    
    def test_select_piece(self):
        """Test selecting a piece."""
        # Select a white pawn (it's white's turn initially)
        self.board.select_piece(6, 0)
        self.assertIsNotNone(self.board.selected_piece)
        self.assertEqual(self.board.selected_piece.piece_type, PAWN)
        self.assertEqual(self.board.selected_piece.color, 'white')
        self.assertGreater(len(self.board.legal_moves), 0)
        
        # Try to select a black piece (should fail as it's white's turn)
        self.board.select_piece(1, 0)
        self.assertIsNone(self.board.selected_piece)
        self.assertEqual(len(self.board.legal_moves), 0)
    
    def test_pawn_moves(self):
        """Test legal moves for a pawn."""
        # White pawn at starting position
        self.board.select_piece(6, 0)
        self.assertIn((5, 0), self.board.legal_moves)  # Move forward one
        self.assertIn((4, 0), self.board.legal_moves)  # Move forward two
        
        # Move the pawn forward one
        self.board.move_piece(5, 0)
        
        # Now it's black's turn, select a black pawn
        self.board.select_piece(1, 0)
        self.assertIn((2, 0), self.board.legal_moves)  # Move forward one
        self.assertIn((3, 0), self.board.legal_moves)  # Move forward two
    
    def test_knight_moves(self):
        """Test legal moves for a knight."""
        # White knight at starting position
        self.board.select_piece(7, 1)
        # Knights can jump over pieces, so should have 2 legal moves initially
        self.assertIn((5, 0), self.board.legal_moves)
        self.assertIn((5, 2), self.board.legal_moves)
    
    def test_move_piece(self):
        """Test moving a piece."""
        # Select and move a white pawn
        self.board.select_piece(6, 0)
        self.assertTrue(self.board.move_piece(4, 0))  # Move forward two
        
        # Verify the pawn moved
        self.assertIsNone(self.board.board[6][0])
        self.assertIsNotNone(self.board.board[4][0])
        self.assertEqual(self.board.board[4][0].piece_type, PAWN)
        self.assertEqual(self.board.board[4][0].color, 'white')
        self.assertTrue(self.board.board[4][0].has_moved)
        
        # Verify it's now black's turn
        self.assertEqual(self.board.turn, 'black')

if __name__ == '__main__':
    unittest.main() 