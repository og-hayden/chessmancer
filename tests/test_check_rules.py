import unittest
from models.chess_board import ChessBoard
from models.chess_piece import ChessPiece
from constants import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING

class TestCheckRules(unittest.TestCase):
    """Test cases for check and checkmate rules."""
    
    def setUp(self):
        """Set up a new chess board for each test."""
        self.board = ChessBoard()
        # Clear the board for custom setups
        self.board.board = [[None for _ in range(8)] for _ in range(8)]
    
    def test_king_in_check(self):
        """Test that the is_king_in_check method correctly identifies when a king is in check."""
        # Set up a board with a white king at e1 and a black bishop at h8 (not attacking)
        self.board.clear_board()
        white_king = ChessPiece(KING, 'white', (7, 4))
        self.board.board[7][4] = white_king  # e1
        
        black_bishop = ChessPiece(BISHOP, 'black', (0, 7))
        self.board.board[0][7] = black_bishop  # h8 - not attacking the king
        
        print("\nDebug test_king_in_check:")
        print(f"King position: (7, 4)")
        print(f"Bishop position: (0, 7)")
        print(f"Is king square attacked: {self.board.is_square_attacked(7, 4, 'black')}")
        
        # King should not be in check
        self.assertFalse(self.board.is_king_in_check('white'))
        
        # Move the bishop to c3 to put the king in check
        self.board.board[0][7] = None  # Remove from h8
        black_bishop.position = (5, 2)  # Update position
        self.board.board[5][2] = black_bishop  # c3 - diagonal attack on e1
        
        print(f"Bishop moved to: (5, 2)")
        print(f"Is king square attacked now: {self.board.is_square_attacked(7, 4, 'black')}")
        
        # King should now be in check
        self.assertTrue(self.board.is_king_in_check('white'))
    
    def test_cannot_move_into_check(self):
        """Test that a king cannot move into a square that is under attack."""
        # Set up a board with a white king at e1 and a black rook at f3
        self.board.clear_board()
        white_king = ChessPiece(KING, 'white', (7, 4))
        self.board.board[7][4] = white_king  # e1
        
        black_rook = ChessPiece(ROOK, 'black', (5, 5))
        self.board.board[5][5] = black_rook  # f3 - controls the f file
        
        # Set the turn to white and select the king
        self.board.turn = 'white'
        self.board.select_piece(7, 4)
        
        # King should not be able to move to f1 (7, 5) as it's under attack by the rook
        self.assertNotIn((7, 5), self.board.legal_moves)  # f1 is under attack
    
    def test_must_move_out_of_check(self):
        """Test that a king in check must move out of check."""
        # Set up a check scenario
        self.board.board[7][4] = ChessPiece(KING, 'white', (7, 4))
        self.board.board[5][4] = ChessPiece(QUEEN, 'black', (5, 4))  # Queen checking the king
        
        # Verify the king is in check
        self.assertTrue(self.board.is_king_in_check('white'))
        
        # Select the king
        self.board.turn = 'white'
        self.board.select_piece(7, 4)
        
        # The king should only have legal moves that get it out of check
        for move in self.board.legal_moves:
            # Temporarily move the king
            row, col = move
            king = self.board.board[7][4]
            old_position = king.position
            self.board.board[7][4] = None
            self.board.board[row][col] = king
            king.position = (row, col)
            
            # Verify the king is no longer in check
            self.assertFalse(self.board.is_king_in_check('white'))
            
            # Restore the board
            king.position = old_position
            self.board.board[row][col] = None
            self.board.board[7][4] = king
    
    def test_can_capture_checking_piece(self):
        """Test that a piece can capture a piece that is putting the king in check."""
        # Set up a board with a white king at e1 and a black queen at e2 (checking the king)
        self.board.clear_board()
        white_king = ChessPiece(KING, 'white', (7, 4))
        self.board.board[7][4] = white_king  # e1
        
        black_queen = ChessPiece(QUEEN, 'black', (6, 4))
        self.board.board[6][4] = black_queen  # e2 - checking the king
        
        # Add a white rook that can capture the queen
        white_rook = ChessPiece(ROOK, 'white', (6, 0))
        self.board.board[6][0] = white_rook  # a2
        
        # King should be in check
        self.assertTrue(self.board.is_king_in_check('white'))
        
        # Rook should be able to capture the queen
        legal_moves = white_rook.get_legal_moves(self.board)
        self.assertIn((6, 4), legal_moves)  # Rook can capture queen at e2
    
    def test_can_block_check(self):
        """Test that a piece can block a check."""
        # Set up a scenario where a piece can block a check
        self.board.board[7][4] = ChessPiece(KING, 'white', (7, 4))
        self.board.board[7][3] = ChessPiece(BISHOP, 'white', (7, 3))  # Bishop that can block the check
        self.board.board[5][4] = ChessPiece(ROOK, 'black', (5, 4))  # Rook checking the king
        
        # Verify the king is in check
        self.assertTrue(self.board.is_king_in_check('white'))
        
        # Select the bishop
        self.board.turn = 'white'
        self.board.select_piece(7, 3)
        
        # The bishop should be able to block the check by moving to (6, 4)
        self.assertIn((6, 4), self.board.legal_moves)
    
    def test_checkmate(self):
        """Test that the is_checkmate method correctly identifies checkmate."""
        # Set up a checkmate scenario: white king at h8, black rooks at g7 and h7
        self.board.board[0][7] = ChessPiece(KING, 'white', (0, 7))
        self.board.board[1][6] = ChessPiece(ROOK, 'black', (1, 6))
        self.board.board[1][7] = ChessPiece(ROOK, 'black', (1, 7))
        
        # Verify the king is in check
        self.assertTrue(self.board.is_king_in_check('white'))
        
        # Verify it's checkmate
        self.assertTrue(self.board.is_checkmate('white'))
    
    def test_not_checkmate(self):
        """Test that the is_checkmate method correctly identifies when it's not checkmate."""
        # Set up a check scenario that is not checkmate: white king at h8, black rook at h7
        self.board.board[0][7] = ChessPiece(KING, 'white', (0, 7))
        self.board.board[1][7] = ChessPiece(ROOK, 'black', (1, 7))
        
        # Verify the king is in check
        self.assertTrue(self.board.is_king_in_check('white'))
        
        # Verify it's not checkmate (king can move to g8)
        self.assertFalse(self.board.is_checkmate('white'))
    
    def test_stalemate(self):
        """Test that the game recognizes stalemate (king not in check but no legal moves)."""
        # Set up a stalemate scenario: white king at a8, black queen at c7
        self.board.board[0][0] = ChessPiece(KING, 'white', (0, 0))
        self.board.board[1][2] = ChessPiece(QUEEN, 'black', (1, 2))
        
        # Verify the king is not in check
        self.assertFalse(self.board.is_king_in_check('white'))
        
        # Select the king
        self.board.turn = 'white'
        self.board.select_piece(0, 0)
        
        # The king should have no legal moves
        self.assertEqual(len(self.board.legal_moves), 0)
        
        # But it's not checkmate
        self.assertFalse(self.board.is_checkmate('white'))

if __name__ == '__main__':
    unittest.main() 