from typing import List, Tuple, Optional, Dict, Any

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

# RPG Extensions for Chess Pieces
class RPGChessPiece(ChessPiece):
    """Extended chess piece with RPG attributes like rarity, level, and durability."""
    
    # Rarity levels
    RARITY_COMMON = "Common"
    RARITY_UNCOMMON = "Uncommon"
    RARITY_RARE = "Rare"
    RARITY_EPIC = "Epic"
    RARITY_LEGENDARY = "Legendary"
    
    # Base durability values by piece type
    BASE_DURABILITY = {
        PAWN: 10,
        KNIGHT: 20,
        BISHOP: 20,
        ROOK: 30,
        QUEEN: 40,
        KING: 50
    }
    
    # Rarity multipliers for stats
    RARITY_MULTIPLIERS = {
        RARITY_COMMON: 1.0,
        RARITY_UNCOMMON: 1.2,
        RARITY_RARE: 1.5,
        RARITY_EPIC: 2.0,
        RARITY_LEGENDARY: 3.0
    }
    
    def __init__(self, piece_type: str, color: str, position: Tuple[int, int], 
                 rarity: str = RARITY_COMMON, level: int = 1, 
                 special_abilities: List[str] = None, equipment: Dict[str, Any] = None):
        """
        Initialize an RPG chess piece with extended attributes.
        
        Args:
            piece_type: Type of chess piece (pawn, knight, etc.)
            color: Color of the piece (white or black)
            position: (row, col) position on the board
            rarity: Rarity level affecting stats
            level: Current level (1-10)
            special_abilities: List of special ability IDs
            equipment: Dictionary of equipped items
        """
        super().__init__(piece_type, color, position)
        self.rarity = rarity
        self.level = min(max(level, 1), 10)  # Ensure level is between 1 and 10
        self.special_abilities = special_abilities or []
        self.equipment = equipment or {}
        
        # Calculate max durability based on piece type, rarity, and level
        base_durability = self.BASE_DURABILITY.get(piece_type, 10)
        rarity_multiplier = self.RARITY_MULTIPLIERS.get(rarity, 1.0)
        level_bonus = (self.level - 1) * 2  # +2 durability per level
        
        self.max_durability = int(base_durability * rarity_multiplier) + level_bonus
        self.current_durability = self.max_durability
        
        # Experience points
        self.xp = 0
        self.xp_to_next_level = self._calculate_xp_for_level(self.level + 1)
        
        # Number of ability slots based on rarity
        self.ability_slots = self._calculate_ability_slots()
        
        # Number of equipment slots based on rarity
        self.equipment_slots = self._calculate_equipment_slots()
    
    def _calculate_ability_slots(self) -> int:
        """Calculate number of ability slots based on rarity."""
        if self.rarity == self.RARITY_COMMON:
            return 0
        elif self.rarity == self.RARITY_UNCOMMON:
            return 1
        elif self.rarity == self.RARITY_RARE:
            return 2
        else:  # Epic or Legendary
            return 3
    
    def _calculate_equipment_slots(self) -> int:
        """Calculate number of equipment slots based on rarity."""
        if self.rarity == self.RARITY_COMMON:
            return 1
        elif self.rarity == self.RARITY_UNCOMMON:
            return 1
        elif self.rarity == self.RARITY_RARE:
            return 2
        else:  # Epic or Legendary
            return 3
    
    def _calculate_xp_for_level(self, level: int) -> int:
        """Calculate XP required to reach a specific level."""
        if level <= 1:
            return 0
        # Exponential XP curve
        return int(100 * (level - 1) ** 1.5)
    
    def add_xp(self, amount: int) -> bool:
        """
        Add XP to the piece and level up if necessary.
        
        Returns:
            bool: True if the piece leveled up, False otherwise
        """
        self.xp += amount
        if self.level < 10 and self.xp >= self.xp_to_next_level:
            self.level_up()
            return True
        return False
    
    def level_up(self) -> None:
        """Level up the piece, increasing its stats."""
        if self.level >= 10:
            return
            
        self.level += 1
        
        # Increase durability
        old_max = self.max_durability
        self.max_durability += 2
        self.current_durability += 2
        
        # Unlock ability slots at levels 3, 6, and 9
        if self.level in [3, 6, 9] and len(self.special_abilities) < self.ability_slots:
            # Potentially unlock a new ability slot if rarity allows
            new_slots = self._calculate_ability_slots()
            if new_slots > len(self.special_abilities):
                # New slot unlocked, but no ability assigned yet
                pass
        
        # Calculate XP for next level
        if self.level < 10:
            self.xp_to_next_level = self._calculate_xp_for_level(self.level + 1)
    
    def take_damage(self, amount: int) -> bool:
        """
        Reduce durability by the given amount.
        
        Returns:
            bool: True if the piece is still usable, False if it's "injured" (0 durability)
        """
        self.current_durability = max(0, self.current_durability - amount)
        return self.current_durability > 0
    
    def repair(self, amount: int) -> None:
        """Repair the piece by the given amount, up to its maximum durability."""
        self.current_durability = min(self.max_durability, self.current_durability + amount)
    
    def get_effectiveness(self) -> float:
        """Calculate the piece's effectiveness based on level and rarity."""
        rarity_bonus = self.RARITY_MULTIPLIERS.get(self.rarity, 1.0)
        level_bonus = 1.0 + (self.level - 1) * 0.05  # +5% per level
        return rarity_bonus * level_bonus
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the piece to a dictionary for storage."""
        return {
            "piece_type": self.piece_type,
            "color": self.color,
            "rarity": self.rarity,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "max_durability": self.max_durability,
            "current_durability": self.current_durability,
            "special_abilities": self.special_abilities.copy(),
            "equipment": self.equipment.copy(),
            "ability_slots": self.ability_slots,
            "equipment_slots": self.equipment_slots
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], position: Tuple[int, int] = (0, 0)) -> 'RPGChessPiece':
        """Create a piece from a dictionary representation."""
        piece = cls(
            piece_type=data["piece_type"],
            color=data["color"],
            position=position,
            rarity=data["rarity"],
            level=data["level"],
            special_abilities=data["special_abilities"],
            equipment=data["equipment"]
        )
        piece.xp = data["xp"]
        piece.xp_to_next_level = data["xp_to_next_level"]
        piece.max_durability = data["max_durability"]
        piece.current_durability = data["current_durability"]
        piece.ability_slots = data["ability_slots"]
        piece.equipment_slots = data["equipment_slots"]
        return piece 