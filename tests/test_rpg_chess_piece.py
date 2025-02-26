import unittest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.chess_piece import RPGChessPiece


class TestRPGChessPiece(unittest.TestCase):
    """Test cases for the RPGChessPiece class."""
    
    def test_init(self):
        """Test initialization of RPGChessPiece."""
        piece = RPGChessPiece("pawn", "white", (6, 0))
        
        self.assertEqual(piece.piece_type, "pawn")
        self.assertEqual(piece.color, "white")
        self.assertEqual(piece.position, (6, 0))
        self.assertEqual(piece.rarity, RPGChessPiece.RARITY_COMMON)
        self.assertEqual(piece.level, 1)
        self.assertEqual(piece.special_abilities, [])
        self.assertEqual(piece.equipment, {})
        
        # Test durability calculation
        self.assertEqual(piece.max_durability, 10)  # Base durability for pawn
        self.assertEqual(piece.current_durability, 10)
    
    def test_rarity_effects(self):
        """Test how rarity affects piece stats."""
        # Common pawn
        common_pawn = RPGChessPiece("pawn", "white", (0, 0), RPGChessPiece.RARITY_COMMON)
        # Legendary pawn
        legendary_pawn = RPGChessPiece("pawn", "white", (0, 0), RPGChessPiece.RARITY_LEGENDARY)
        
        # Test durability differences
        self.assertEqual(common_pawn.max_durability, 10)
        self.assertEqual(legendary_pawn.max_durability, 30)  # 10 * 3.0 rarity multiplier
        
        # Test ability slots
        self.assertEqual(common_pawn.ability_slots, 0)
        self.assertEqual(legendary_pawn.ability_slots, 3)
        
        # Test equipment slots
        self.assertEqual(common_pawn.equipment_slots, 1)
        self.assertEqual(legendary_pawn.equipment_slots, 3)
        
        # Test effectiveness
        self.assertAlmostEqual(common_pawn.get_effectiveness(), 1.0)
        self.assertAlmostEqual(legendary_pawn.get_effectiveness(), 3.0)
    
    def test_level_up(self):
        """Test leveling up a piece."""
        piece = RPGChessPiece("knight", "black", (0, 0))
        
        # Initial state
        self.assertEqual(piece.level, 1)
        self.assertEqual(piece.max_durability, 20)
        
        # Add XP to level up
        initial_xp_needed = piece.xp_to_next_level
        self.assertEqual(initial_xp_needed, 100)  # Level 1 to 2 requires 100 XP
        
        # Add just enough XP to level up
        leveled_up = piece.add_xp(100)
        self.assertTrue(leveled_up)
        self.assertEqual(piece.level, 2)
        self.assertEqual(piece.max_durability, 22)  # +2 durability per level
        self.assertEqual(piece.current_durability, 22)
        
        # Test XP for next level
        self.assertGreater(piece.xp_to_next_level, initial_xp_needed)
    
    def test_take_damage(self):
        """Test taking damage and repairing."""
        piece = RPGChessPiece("rook", "white", (0, 0))
        
        # Initial durability
        self.assertEqual(piece.current_durability, 30)
        self.assertEqual(piece.max_durability, 30)
        
        # Take damage
        still_usable = piece.take_damage(10)
        self.assertTrue(still_usable)
        self.assertEqual(piece.current_durability, 20)
        
        # Take more damage
        still_usable = piece.take_damage(20)
        self.assertFalse(still_usable)
        self.assertEqual(piece.current_durability, 0)
        
        # Repair
        piece.repair(15)
        self.assertEqual(piece.current_durability, 15)
        
        # Repair beyond max
        piece.repair(20)
        self.assertEqual(piece.current_durability, 30)  # Capped at max_durability
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        original = RPGChessPiece(
            piece_type="queen",
            color="black",
            position=(3, 3),
            rarity=RPGChessPiece.RARITY_EPIC,
            level=5,
            special_abilities=["teleport", "phantom_strike"],
            equipment={"weapon": "magic_staff", "armor": "royal_cloak"}
        )
        
        # Add some XP
        original.add_xp(50)
        
        # Convert to dict
        piece_dict = original.to_dict()
        
        # Create new piece from dict
        new_position = (7, 7)
        recreated = RPGChessPiece.from_dict(piece_dict, new_position)
        
        # Check all attributes were preserved
        self.assertEqual(recreated.piece_type, "queen")
        self.assertEqual(recreated.color, "black")
        self.assertEqual(recreated.position, new_position)  # Position should be updated
        self.assertEqual(recreated.rarity, RPGChessPiece.RARITY_EPIC)
        self.assertEqual(recreated.level, 5)
        self.assertEqual(recreated.special_abilities, ["teleport", "phantom_strike"])
        self.assertEqual(recreated.equipment, {"weapon": "magic_staff", "armor": "royal_cloak"})
        self.assertEqual(recreated.xp, 50)
        self.assertEqual(recreated.max_durability, original.max_durability)
        self.assertEqual(recreated.current_durability, original.current_durability)


if __name__ == "__main__":
    unittest.main() 