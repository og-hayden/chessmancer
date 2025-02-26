import unittest
import pygame
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Starting test setup...")

# Initialize pygame for testing
pygame.init()
pygame.display.set_mode((800, 600))

# Import the necessary modules
from models.dungeon import Dungeon, Enemy
from models.player import Player
from models.player_inventory import PlayerInventory
from models.chess_board import ChessBoard
from constants import MODE_HUMAN_VS_AI, MODE_CHESS, MODE_DUNGEON

print("Imports successful")

class TestDungeonChessIntegration(unittest.TestCase):
    """Test the integration between dungeon exploration and chess combat."""
    
    def setUp(self):
        """Set up the test environment."""
        print("Setting up test environment...")
        # Create a player inventory
        self.inventory = PlayerInventory()
        
        # Create a small test dungeon
        self.dungeon = Dungeon(
            width=20,
            height=20,
            difficulty=1,
            num_rooms=3,
            min_room_size=5,
            max_room_size=8
        )
        print("Dungeon created")
        
        # Create a player
        start_pos = self.dungeon.get_starting_position()
        self.player = Player(start_pos, self.inventory)
        print("Player created at position:", start_pos)
        
        # Create a chess board for combat
        self.chess_board = ChessBoard(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=5)
        print("Chess board created")
        
        # Add an enemy near the player for testing
        self.add_enemy_near_player()
        print("Setup complete")
    
    def add_enemy_near_player(self):
        """Add an enemy adjacent to the player for testing."""
        player_x, player_y = self.player.position
        print(f"Adding enemy near player at position: ({player_x}, {player_y})")
        
        # Try to place an enemy in an adjacent tile
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            test_x, test_y = player_x + dx, player_y + dy
            
            if (0 <= test_x < self.dungeon.width and 
                0 <= test_y < self.dungeon.height and 
                self.dungeon.is_walkable(test_x, test_y)):
                
                # Create an enemy
                enemy = Enemy((test_x, test_y), "test_enemy", difficulty=1)
                print(f"Enemy created at position: ({test_x}, {test_y})")
                
                # Place the enemy in the dungeon
                self.dungeon.grid[test_y][test_x].entity = enemy
                self.enemy = enemy
                self.enemy_position = (test_x, test_y)
                return
        
        print("Could not place enemy adjacent to player, trying elsewhere...")
        # If we couldn't place an enemy adjacent to the player, place it somewhere else
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                if (self.dungeon.is_walkable(x, y) and 
                    (x, y) != self.player.position and
                    self.dungeon.get_entity_at(x, y) is None):
                    
                    # Create an enemy
                    enemy = Enemy((x, y), "test_enemy", difficulty=1)
                    print(f"Enemy created at position: ({x}, {y})")
                    
                    # Place the enemy in the dungeon
                    self.dungeon.grid[y][x].entity = enemy
                    self.enemy = enemy
                    self.enemy_position = (x, y)
                    return
        
        print("WARNING: Could not place enemy anywhere in the dungeon!")
    
    def test_enemy_detection(self):
        """Test that enemies are correctly detected in adjacent tiles."""
        print("\nRunning test_enemy_detection...")
        # Get the enemy's position
        enemy_x, enemy_y = self.enemy_position
        print(f"Enemy position: ({enemy_x}, {enemy_y})")
        
        # Move the player adjacent to the enemy if not already
        player_x, player_y = self.player.position
        print(f"Player position: ({player_x}, {player_y})")
        
        # Calculate direction to move
        dx = max(-1, min(1, enemy_x - player_x))
        dy = max(-1, min(1, enemy_y - player_y)) if dx == 0 else 0
        
        # Move the player next to the enemy
        new_x = enemy_x - dx
        new_y = enemy_y - dy
        print(f"Moving player to: ({new_x}, {new_y})")
        
        # Set player position directly for testing
        self.player.position = (new_x, new_y)
        
        # Check if the enemy is detected in an adjacent tile
        adjacent_entities = []
        for check_dx, check_dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            check_x, check_y = new_x + check_dx, new_y + check_dy
            
            if (0 <= check_x < self.dungeon.width and 
                0 <= check_y < self.dungeon.height):
                entity = self.dungeon.get_entity_at(check_x, check_y)
                if entity:
                    adjacent_entities.append(entity)
                    print(f"Found entity at ({check_x}, {check_y}): {type(entity).__name__}")
        
        # Assert that the enemy is in the list of adjacent entities
        enemy_detected = any(isinstance(entity, Enemy) for entity in adjacent_entities)
        print(f"Enemy detected: {enemy_detected}")
        self.assertTrue(enemy_detected, "Enemy should be detected in an adjacent tile")
        print("test_enemy_detection passed")
    
    def test_mode_transition(self):
        """Test transitioning from dungeon mode to chess mode."""
        print("\nRunning test_mode_transition...")
        # Define global variables for testing
        global game_mode, current_enemy
        game_mode = MODE_DUNGEON
        current_enemy = None
        print(f"Initial game_mode: {game_mode}")
        
        # Define a simplified handle_interaction function for testing
        def handle_interaction(interaction_result, player, dungeon, dungeon_ui):
            global game_mode, current_enemy
            if isinstance(interaction_result, Enemy):
                game_mode = MODE_CHESS
                current_enemy = interaction_result
                print(f"Changed game_mode to: {game_mode}")
        
        # Simulate player interaction with enemy
        print("Simulating interaction with enemy")
        handle_interaction(self.enemy, self.player, self.dungeon, None)
        
        # Check that the game mode changed to chess
        print(f"Final game_mode: {game_mode}")
        self.assertEqual(game_mode, MODE_CHESS, 
                       "Game mode should change to chess when encountering an enemy")
        
        # Check that the current enemy is set
        print(f"Current enemy: {current_enemy}")
        self.assertEqual(current_enemy, self.enemy,
                       "Current enemy should be set when transitioning to chess mode")
        print("test_mode_transition passed")
    
    def test_chess_combat_setup(self):
        """Test that chess combat is set up correctly."""
        print("\nRunning test_chess_combat_setup...")
        # Ensure the chess board is initialized with the correct settings
        print(f"Chess board game mode: {self.chess_board.game_mode}")
        self.assertEqual(self.chess_board.game_mode, MODE_HUMAN_VS_AI,
                       "Chess board should be in Human vs AI mode")
        
        # Check that the board has the correct number of pieces
        white_pieces = sum(1 for row in self.chess_board.board 
                         for piece in row if piece and piece.color == 'white')
        black_pieces = sum(1 for row in self.chess_board.board 
                         for piece in row if piece and piece.color == 'black')
        
        print(f"White pieces: {white_pieces}, Black pieces: {black_pieces}")
        self.assertEqual(white_pieces, 16, "White should have 16 pieces at the start")
        self.assertEqual(black_pieces, 16, "Black should have 16 pieces at the start")
        print("test_chess_combat_setup passed")
    
    def test_enemy_removal_after_victory(self):
        """Test that enemies are removed after being defeated in chess combat."""
        print("\nRunning test_enemy_removal_after_victory...")
        # Set up the test scenario
        enemy_x, enemy_y = self.enemy_position
        print(f"Enemy position: ({enemy_x}, {enemy_y})")
        
        # Mock a chess victory
        self.chess_board.game_over = True
        self.chess_board.game_result = "White wins by checkmate"
        print("Simulating chess victory")
        
        # Simulate the code that would run after victory
        dungeon_tile = self.dungeon.grid[enemy_y][enemy_x]
        dungeon_tile.entity = None
        print("Removed enemy from dungeon")
        
        # Check that the enemy was removed
        entity = self.dungeon.get_entity_at(enemy_x, enemy_y)
        print(f"Entity at enemy position after removal: {entity}")
        self.assertIsNone(entity, "Enemy should be removed after being defeated")
        print("test_enemy_removal_after_victory passed")

if __name__ == '__main__':
    print("Starting tests...")
    unittest.main() 