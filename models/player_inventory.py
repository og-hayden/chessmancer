import json
import os
import random
from typing import List, Dict, Any, Optional, Tuple

from models.chess_piece import RPGChessPiece


class PlayerInventory:
    """Manages the player's inventory of collected chess pieces and items."""
    
    def __init__(self, save_file: str = "player_inventory.json"):
        """
        Initialize the player's inventory.
        
        Args:
            save_file: Path to the save file for the inventory
        """
        self.save_file = save_file
        self.active_pieces: List[RPGChessPiece] = []  # Pieces in the active roster
        self.reserve_pieces: List[RPGChessPiece] = []  # Pieces in storage
        self.gold = 100  # Starting gold
        self.command_stat = 10  # Starting command stat (determines how many pieces can be deployed)
        self.tactics_stat = 5  # Starting tactics stat
        self.perception_stat = 5  # Starting perception stat
        self.arcana_stat = 5  # Starting arcana stat
        
        # Try to load existing inventory
        self.load_inventory()
        
        # If no inventory exists, create a starter set
        if not self.active_pieces and not self.reserve_pieces:
            self._create_starter_set()
    
    def _create_starter_set(self) -> None:
        """Create a starter set of pieces for a new player."""
        # Create a king (always needed)
        king = RPGChessPiece(
            piece_type="king",
            color="white",
            position=(0, 0),  # Position doesn't matter in inventory
            rarity=RPGChessPiece.RARITY_UNCOMMON,  # Start with an uncommon king
            level=1
        )
        
        # Create 4 pawns
        pawns = [
            RPGChessPiece(
                piece_type="pawn",
                color="white",
                position=(0, 0),
                rarity=RPGChessPiece.RARITY_COMMON,
                level=1
            ) for _ in range(4)
        ]
        
        # Create 1 knight
        knight = RPGChessPiece(
            piece_type="knight",
            color="white",
            position=(0, 0),
            rarity=RPGChessPiece.RARITY_COMMON,
            level=1
        )
        
        # Add pieces to active roster
        self.active_pieces = [king] + pawns + [knight]
    
    def add_piece(self, piece: RPGChessPiece, to_active: bool = False) -> None:
        """
        Add a piece to the inventory.
        
        Args:
            piece: The piece to add
            to_active: If True, add to active roster; otherwise, add to reserve
        """
        if to_active and len(self.active_pieces) < self.command_stat:
            self.active_pieces.append(piece)
        else:
            self.reserve_pieces.append(piece)
    
    def remove_piece(self, piece_index: int, from_active: bool = True) -> Optional[RPGChessPiece]:
        """
        Remove a piece from the inventory.
        
        Args:
            piece_index: Index of the piece to remove
            from_active: If True, remove from active roster; otherwise, remove from reserve
            
        Returns:
            The removed piece, or None if the index is invalid
        """
        pieces = self.active_pieces if from_active else self.reserve_pieces
        
        if 0 <= piece_index < len(pieces):
            return pieces.pop(piece_index)
        
        return None
    
    def move_to_active(self, reserve_index: int) -> bool:
        """
        Move a piece from reserve to active roster.
        
        Args:
            reserve_index: Index of the piece in reserve
            
        Returns:
            True if successful, False if active roster is full or index is invalid
        """
        if len(self.active_pieces) >= self.command_stat:
            return False
        
        piece = self.remove_piece(reserve_index, from_active=False)
        if piece:
            self.active_pieces.append(piece)
            return True
        
        return False
    
    def move_to_reserve(self, active_index: int) -> bool:
        """
        Move a piece from active roster to reserve.
        
        Args:
            active_index: Index of the piece in active roster
            
        Returns:
            True if successful, False if index is invalid
        """
        piece = self.remove_piece(active_index, from_active=True)
        if piece:
            self.reserve_pieces.append(piece)
            return True
        
        return False
    
    def get_active_pieces_for_battle(self) -> List[RPGChessPiece]:
        """
        Get a copy of active pieces for battle.
        
        Returns:
            List of active pieces with positions reset
        """
        battle_pieces = []
        for piece in self.active_pieces:
            # Create a copy of the piece with position (0,0)
            piece_dict = piece.to_dict()
            battle_piece = RPGChessPiece.from_dict(piece_dict, (0, 0))
            battle_pieces.append(battle_piece)
        
        return battle_pieces
    
    def add_gold(self, amount: int) -> None:
        """Add gold to the inventory."""
        self.gold += amount
    
    def spend_gold(self, amount: int) -> bool:
        """
        Spend gold from the inventory.
        
        Args:
            amount: Amount of gold to spend
            
        Returns:
            True if successful, False if not enough gold
        """
        if self.gold >= amount:
            self.gold -= amount
            return True
        
        return False
    
    def increase_command(self, amount: int = 1) -> None:
        """Increase the command stat."""
        self.command_stat += amount
    
    def increase_stat(self, stat_name: str, amount: int = 1) -> bool:
        """
        Increase a player stat.
        
        Args:
            stat_name: Name of the stat to increase ('command', 'tactics', 'perception', 'arcana')
            amount: Amount to increase the stat by
            
        Returns:
            True if successful, False if stat name is invalid
        """
        if stat_name == 'command':
            self.command_stat += amount
        elif stat_name == 'tactics':
            self.tactics_stat += amount
        elif stat_name == 'perception':
            self.perception_stat += amount
        elif stat_name == 'arcana':
            self.arcana_stat += amount
        else:
            return False
        
        return True
    
    def generate_random_piece(self, min_rarity: str = RPGChessPiece.RARITY_COMMON, 
                             max_rarity: str = RPGChessPiece.RARITY_RARE) -> RPGChessPiece:
        """
        Generate a random chess piece for rewards.
        
        Args:
            min_rarity: Minimum rarity level
            max_rarity: Maximum rarity level
            
        Returns:
            A randomly generated chess piece
        """
        # Define rarity weights (higher rarities are less common)
        rarity_weights = {
            RPGChessPiece.RARITY_COMMON: 60,
            RPGChessPiece.RARITY_UNCOMMON: 30,
            RPGChessPiece.RARITY_RARE: 8,
            RPGChessPiece.RARITY_EPIC: 1.5,
            RPGChessPiece.RARITY_LEGENDARY: 0.5
        }
        
        # Filter rarities based on min/max
        rarities = [r for r in rarity_weights.keys() 
                   if self._rarity_value(r) >= self._rarity_value(min_rarity) and 
                   self._rarity_value(r) <= self._rarity_value(max_rarity)]
        
        # Get weights for available rarities
        weights = [rarity_weights[r] for r in rarities]
        
        # Normalize weights
        total = sum(weights)
        normalized_weights = [w/total for w in weights]
        
        # Select rarity
        rarity = random.choices(rarities, weights=normalized_weights, k=1)[0]
        
        # Select piece type (weighted)
        piece_weights = {
            "pawn": 50,
            "knight": 15,
            "bishop": 15,
            "rook": 10,
            "queen": 8,
            "king": 2
        }
        
        piece_types = list(piece_weights.keys())
        piece_type_weights = list(piece_weights.values())
        total = sum(piece_type_weights)
        normalized_weights = [w/total for w in piece_type_weights]
        
        piece_type = random.choices(piece_types, weights=normalized_weights, k=1)[0]
        
        # Select color (50/50)
        color = random.choice(["white", "black"])
        
        # Create the piece
        return RPGChessPiece(
            piece_type=piece_type,
            color=color,
            position=(0, 0),
            rarity=rarity,
            level=1
        )
    
    def _rarity_value(self, rarity: str) -> int:
        """Convert rarity string to numeric value for comparison."""
        rarity_values = {
            RPGChessPiece.RARITY_COMMON: 1,
            RPGChessPiece.RARITY_UNCOMMON: 2,
            RPGChessPiece.RARITY_RARE: 3,
            RPGChessPiece.RARITY_EPIC: 4,
            RPGChessPiece.RARITY_LEGENDARY: 5
        }
        return rarity_values.get(rarity, 0)
    
    def save_inventory(self) -> bool:
        """
        Save the inventory to a file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "gold": self.gold,
                "command_stat": self.command_stat,
                "tactics_stat": self.tactics_stat,
                "perception_stat": self.perception_stat,
                "arcana_stat": self.arcana_stat,
                "active_pieces": [piece.to_dict() for piece in self.active_pieces],
                "reserve_pieces": [piece.to_dict() for piece in self.reserve_pieces]
            }
            
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving inventory: {e}")
            return False
    
    def load_inventory(self) -> bool:
        """
        Load the inventory from a file.
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.save_file):
            return False
        
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
            
            self.gold = data.get("gold", 100)
            self.command_stat = data.get("command_stat", 10)
            self.tactics_stat = data.get("tactics_stat", 5)
            self.perception_stat = data.get("perception_stat", 5)
            self.arcana_stat = data.get("arcana_stat", 5)
            
            self.active_pieces = [
                RPGChessPiece.from_dict(piece_data) 
                for piece_data in data.get("active_pieces", [])
            ]
            
            self.reserve_pieces = [
                RPGChessPiece.from_dict(piece_data) 
                for piece_data in data.get("reserve_pieces", [])
            ]
            
            return True
        except Exception as e:
            print(f"Error loading inventory: {e}")
            return False 