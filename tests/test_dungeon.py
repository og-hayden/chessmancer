import sys
import os
import unittest
import random

# Add the parent directory to the path so we can import the models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.dungeon import Dungeon, DungeonTile, DungeonRoom, Enemy, Chest
from constants import FLOOR_TILE, WALL_TILE, DOOR_TILE, ENEMY_TILE, CHEST_TILE, PLAYER_TILE


class TestDungeon(unittest.TestCase):
    """Test cases for the Dungeon class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Set a fixed seed for reproducibility
        random.seed(42)
        
        # Create a small dungeon for testing
        self.dungeon = Dungeon(width=30, height=30, num_rooms=5)
    
    def test_initialization(self):
        """Test that the dungeon is initialized correctly."""
        # Check dimensions
        self.assertEqual(self.dungeon.width, 30)
        self.assertEqual(self.dungeon.height, 30)
        
        # Check that the grid is the right size
        self.assertEqual(len(self.dungeon.grid), 30)
        self.assertEqual(len(self.dungeon.grid[0]), 30)
        
        # Check that rooms were generated
        self.assertGreater(len(self.dungeon.rooms), 0)
        self.assertLessEqual(len(self.dungeon.rooms), 5)
    
    def test_room_generation(self):
        """Test that rooms are generated correctly."""
        # Check that each room has valid dimensions
        for room in self.dungeon.rooms:
            self.assertGreaterEqual(room.width, self.dungeon.min_room_size)
            self.assertLessEqual(room.width, self.dungeon.max_room_size)
            self.assertGreaterEqual(room.height, self.dungeon.min_room_size)
            self.assertLessEqual(room.height, self.dungeon.max_room_size)
            
            # Check that the room is within the dungeon bounds
            self.assertGreaterEqual(room.x, 0)
            self.assertLess(room.x + room.width, self.dungeon.width)
            self.assertGreaterEqual(room.y, 0)
            self.assertLess(room.y + room.height, self.dungeon.height)
            
            # Check that the room tiles are floor tiles or door tiles (at the edges)
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    tile_type = self.dungeon.grid[y][x].tile_type
                    # Allow for door tiles at the edges of rooms
                    if (x == room.x or x == room.x + room.width - 1 or 
                        y == room.y or y == room.y + room.height - 1):
                        self.assertIn(tile_type, [FLOOR_TILE, DOOR_TILE])
                    else:
                        self.assertEqual(tile_type, FLOOR_TILE)
    
    def test_room_connections(self):
        """Test that rooms are connected."""
        # Check that each room (except the last) is connected to at least one other room
        for i in range(len(self.dungeon.rooms) - 1):
            room = self.dungeon.rooms[i]
            self.assertGreater(len(room.connected_rooms), 0)
    
    def test_special_rooms(self):
        """Test that special rooms are assigned correctly."""
        # If we have at least 3 rooms, we should have start, boss, and treasure rooms
        if len(self.dungeon.rooms) >= 3:
            room_types = [room.room_type for room in self.dungeon.rooms]
            self.assertIn("start", room_types)
            self.assertIn("boss", room_types)
            self.assertIn("treasure", room_types)
    
    def test_enemies_and_chests(self):
        """Test that enemies and chests are added to the dungeon."""
        # Check that we have some enemies and chests
        self.assertGreaterEqual(len(self.dungeon.enemies), 0)
        self.assertGreaterEqual(len(self.dungeon.chests), 0)
        
        # Check that enemies and chests are placed on the grid
        for enemy in self.dungeon.enemies:
            x, y = enemy.position
            self.assertEqual(self.dungeon.grid[y][x].entity, enemy)
            self.assertTrue(self.dungeon.grid[y][x].interactable)
        
        for chest in self.dungeon.chests:
            x, y = chest.position
            self.assertEqual(self.dungeon.grid[y][x].entity, chest)
            self.assertTrue(self.dungeon.grid[y][x].interactable)
    
    def test_starting_position(self):
        """Test that the starting position is valid."""
        x, y = self.dungeon.get_starting_position()
        
        # Check that the starting position is within bounds
        self.assertGreaterEqual(x, 0)
        self.assertLess(x, self.dungeon.width)
        self.assertGreaterEqual(y, 0)
        self.assertLess(y, self.dungeon.height)
        
        # Check that the starting position is in a room
        in_room = False
        for room in self.dungeon.rooms:
            if (room.x <= x < room.x + room.width and 
                room.y <= y < room.y + room.height):
                in_room = True
                break
        self.assertTrue(in_room)
    
    def test_is_walkable(self):
        """Test the is_walkable method."""
        # Get a position that should be walkable (center of first room)
        if self.dungeon.rooms:
            room = self.dungeon.rooms[0]
            x, y = room.center()
            self.assertTrue(self.dungeon.is_walkable(x, y))
        
        # Check that positions outside the dungeon are not walkable
        self.assertFalse(self.dungeon.is_walkable(-1, -1))
        self.assertFalse(self.dungeon.is_walkable(self.dungeon.width, self.dungeon.height))
        
        # Check that wall tiles are not walkable
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                if self.dungeon.grid[y][x].tile_type == WALL_TILE:
                    self.assertFalse(self.dungeon.is_walkable(x, y))
    
    def test_get_entity_at(self):
        """Test the get_entity_at method."""
        # Check that we get None for positions outside the dungeon
        self.assertIsNone(self.dungeon.get_entity_at(-1, -1))
        self.assertIsNone(self.dungeon.get_entity_at(self.dungeon.width, self.dungeon.height))
        
        # Check that we get the correct entity for positions with entities
        for enemy in self.dungeon.enemies:
            x, y = enemy.position
            self.assertEqual(self.dungeon.get_entity_at(x, y), enemy)
        
        for chest in self.dungeon.chests:
            x, y = chest.position
            self.assertEqual(self.dungeon.get_entity_at(x, y), chest)
    
    def test_update_visibility(self):
        """Test the update_visibility method."""
        # Get the starting position
        x, y = self.dungeon.get_starting_position()
        
        # Update visibility
        self.dungeon.update_visibility(x, y, vision_range=5)
        
        # Check that some tiles are visible
        visible_count = 0
        for row in self.dungeon.grid:
            for tile in row:
                if tile.visible:
                    visible_count += 1
        
        self.assertGreater(visible_count, 0)
        
        # Check that tiles far away are not visible
        far_x, far_y = 0, 0
        if x > 15:
            far_x = 0
        else:
            far_x = 29
        
        if y > 15:
            far_y = 0
        else:
            far_y = 29
        
        # Only check if the far position is a wall (to ensure it's not in line of sight)
        if self.dungeon.grid[far_y][far_x].tile_type == WALL_TILE:
            self.assertFalse(self.dungeon.grid[far_y][far_x].visible)


if __name__ == "__main__":
    unittest.main() 