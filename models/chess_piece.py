from typing import List, Tuple, Optional

from constants import (
    BOARD_SIZE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
)

class ChessPiece:
    """Represents a chess piece with its type, color, and position."""
    
    def __init__(self, piece_type: str, color: str, position: Tuple[int, int]):
        self.piece_type = piece_type
        self.color = color
        self.position = position
        self.has_moved = False
        
    def get_image_key(self) -> str:
        """Return the key to look up the piece's image."""
        return f'{self.color}_{self.piece_type}'
    
    def get_legal_moves(self, board: 'ChessBoard') -> List[Tuple[int, int]]:
        """Return a list of legal moves for this piece."""
        row, col = self.position
        moves = []
        
        if self.piece_type == PAWN:
            direction = -1 if self.color == 'white' else 1
            
            # Move forward one square
            if 0 <= row + direction < BOARD_SIZE:
                if board.board[row + direction][col] is None:
                    moves.append((row + direction, col))
                    
                    # Move forward two squares from starting position
                    if ((self.color == 'white' and row == 6) or 
                        (self.color == 'black' and row == 1)):
                        if (0 <= row + 2 * direction < BOARD_SIZE and 
                            board.board[row + 2 * direction][col] is None):
                            moves.append((row + 2 * direction, col))
            
            # Capture diagonally
            for dc in [-1, 1]:
                if 0 <= row + direction < BOARD_SIZE and 0 <= col + dc < BOARD_SIZE:
                    target = board.board[row + direction][col + dc]
                    if target is not None and target.color != self.color:
                        moves.append((row + direction, col + dc))
            
            # En passant capture
            if board.last_pawn_double_move is not None:
                en_passant_row, en_passant_col = board.last_pawn_double_move
                
                # Check if the last pawn move was adjacent to this pawn
                if (abs(col - en_passant_col) == 1 and row == en_passant_row):
                    # The en passant capture moves the pawn diagonally behind the enemy pawn
                    moves.append((row + direction, en_passant_col))
        
        elif self.piece_type == KNIGHT:
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                    target = board.board[new_row][new_col]
                    if target is None or target.color != self.color:
                        moves.append((new_row, new_col))
        
        elif self.piece_type in [BISHOP, ROOK, QUEEN]:
            directions = []
            
            if self.piece_type in [BISHOP, QUEEN]:
                directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])  # Diagonals
                
            if self.piece_type in [ROOK, QUEEN]:
                directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])  # Horizontals and verticals
            
            for dr, dc in directions:
                for i in range(1, BOARD_SIZE):
                    new_row, new_col = row + i * dr, col + i * dc
                    
                    if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE):
                        break
                    
                    target = board.board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target.color != self.color:
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        
        elif self.piece_type == KING:
            king_moves = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]
            
            for dr, dc in king_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                    target = board.board[new_row][new_col]
                    if target is None or target.color != self.color:
                        moves.append((new_row, new_col))
            
            # Check for castling
            if not self.has_moved:
                # Kingside castling (O-O)
                if self._can_castle_kingside(board):
                    # Add the castling move (king moves two squares to the right)
                    moves.append((row, col + 2))
                
                # Queenside castling (O-O-O)
                if self._can_castle_queenside(board):
                    # Add the castling move (king moves two squares to the left)
                    moves.append((row, col - 2))
        
        return moves
    
    def _can_castle_kingside(self, board: 'ChessBoard') -> bool:
        """Check if kingside castling is possible."""
        row, col = self.position
        
        # Check if the rook is in the correct position and hasn't moved
        rook_col = 7
        rook = board.board[row][rook_col]
        if not rook or rook.piece_type != ROOK or rook.has_moved:
            return False
        
        # Check if squares between king and rook are empty
        for c in range(col + 1, rook_col):
            if board.board[row][c] is not None:
                return False
        
        # Check if king is in check
        if self._is_square_attacked(board, row, col):
            return False
        
        # Check if squares king moves through are attacked
        for c in range(col + 1, col + 3):  # King moves through col+1 and lands on col+2
            if self._is_square_attacked(board, row, c):
                return False
        
        return True
    
    def _can_castle_queenside(self, board: 'ChessBoard') -> bool:
        """Check if queenside castling is possible."""
        row, col = self.position
        
        # Check if the rook is in the correct position and hasn't moved
        rook_col = 0
        rook = board.board[row][rook_col]
        if not rook or rook.piece_type != ROOK or rook.has_moved:
            return False
        
        # Check if squares between king and rook are empty
        for c in range(rook_col + 1, col):
            if board.board[row][c] is not None:
                return False
        
        # Check if king is in check
        if self._is_square_attacked(board, row, col):
            return False
        
        # Check if squares king moves through are attacked
        for c in range(col - 1, col - 3, -1):  # King moves through col-1 and lands on col-2
            if self._is_square_attacked(board, row, c):
                return False
        
        return True
    
    def _is_square_attacked(self, board: 'ChessBoard', row: int, col: int) -> bool:
        """Check if a square is attacked by any opponent's piece."""
        opponent_color = 'black' if self.color == 'white' else 'white'
        
        # Check for attacks from pawns
        pawn_direction = 1 if opponent_color == 'black' else -1
        for dc in [-1, 1]:
            attack_row = row + pawn_direction
            attack_col = col + dc
            if 0 <= attack_row < BOARD_SIZE and 0 <= attack_col < BOARD_SIZE:
                piece = board.board[attack_row][attack_col]
                if piece and piece.piece_type == PAWN and piece.color == opponent_color:
                    return True
        
        # Check for attacks from knights
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_moves:
            attack_row, attack_col = row + dr, col + dc
            if 0 <= attack_row < BOARD_SIZE and 0 <= attack_col < BOARD_SIZE:
                piece = board.board[attack_row][attack_col]
                if piece and piece.piece_type == KNIGHT and piece.color == opponent_color:
                    return True
        
        # Check for attacks from kings (for adjacent squares)
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dr, dc in king_moves:
            attack_row, attack_col = row + dr, col + dc
            if 0 <= attack_row < BOARD_SIZE and 0 <= attack_col < BOARD_SIZE:
                piece = board.board[attack_row][attack_col]
                if piece and piece.piece_type == KING and piece.color == opponent_color:
                    return True
        
        # Check for attacks from sliding pieces (bishop, rook, queen)
        # Directions for all sliding pieces
        directions = []
        
        # Bishop and Queen directions (diagonals)
        directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
        
        # Rook and Queen directions (horizontals and verticals)
        directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])
        
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                attack_row, attack_col = row + i * dr, col + i * dc
                
                if not (0 <= attack_row < BOARD_SIZE and 0 <= attack_col < BOARD_SIZE):
                    break
                
                piece = board.board[attack_row][attack_col]
                if piece:
                    if piece.color == opponent_color:
                        # Check if this piece can attack in this direction
                        can_attack = False
                        
                        # Bishops attack diagonally
                        if piece.piece_type == BISHOP and abs(dr) == abs(dc):
                            can_attack = True
                        
                        # Rooks attack horizontally and vertically
                        elif piece.piece_type == ROOK and (dr == 0 or dc == 0):
                            can_attack = True
                        
                        # Queens attack in all directions
                        elif piece.piece_type == QUEEN:
                            can_attack = True
                        
                        if can_attack:
                            return True
                    
                    # If we hit any piece (even our own), we can't be attacked from beyond it
                    break
        
        return False 