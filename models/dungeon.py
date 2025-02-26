import random
from typing import List, Dict, Tuple, Optional, Set, Any
import pygame
import numpy as np

from constants import TILE_SIZE, FLOOR_TILE, WALL_TILE, DOOR_TILE, ENEMY_TILE, CHEST_TILE, PLAYER_TILE


class DungeonTile:
    """Represents a single tile in the dungeon."""
    
    def __init__(self, tile_type: str, walkable: bool = True, 
                 entity: Optional[Any] = None, interactable: bool = False):
        """
        Initialize a dungeon tile.
        
        Args:
            tile_type: Type of tile (floor, wall, door, etc.)
            walkable: Whether the player can walk on this tile
            entity: Optional entity on this tile (enemy, chest, etc.)
            interactable: Whether this tile can be interacted with
        """
        self.tile_type = tile_type
        self.walkable = walkable
        self.entity = entity
        self.interactable = interactable
        self.discovered = False
        self.visible = False


class DungeonRoom:
    """Represents a room in the dungeon."""
    
    def __init__(self, x: int, y: int, width: int, height: int, room_type: str = "normal"):
        """
        Initialize a dungeon room.
        
        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of the room in tiles
            height: Height of the room in tiles
            room_type: Type of room (normal, treasure, boss, etc.)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.room_type = room_type
        self.connected_rooms: Set[DungeonRoom] = set()
        
    def center(self) -> Tuple[int, int]:
        """Get the center coordinates of the room."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def overlaps(self, other: 'DungeonRoom') -> bool:
        """Check if this room overlaps with another room."""
        return (self.x <= other.x + other.width and
                self.x + self.width >= other.x and
                self.y <= other.y + other.height and
                self.y + self.height >= other.y)
    
    def connect_to(self, other: 'DungeonRoom') -> None:
        """Connect this room to another room."""
        self.connected_rooms.add(other)
        other.connected_rooms.add(self)


class Enemy:
    """Represents an enemy in the dungeon."""
    
    def __init__(self, position: Tuple[int, int], enemy_type: str, difficulty: int = 1):
        """
        Initialize an enemy.
        
        Args:
            position: (x, y) position in the dungeon
            enemy_type: Type of enemy
            difficulty: Difficulty level (affects combat)
        """
        self.position = position
        self.enemy_type = enemy_type
        self.difficulty = difficulty
        self.defeated = False
        
        # Enemy's chess pieces will be generated when combat starts
        self.pieces = []


class Chest:
    """Represents a treasure chest in the dungeon."""
    
    def __init__(self, position: Tuple[int, int], chest_type: str = "normal"):
        """
        Initialize a chest.
        
        Args:
            position: (x, y) position in the dungeon
            chest_type: Type of chest (normal, rare, etc.)
        """
        self.position = position
        self.chest_type = chest_type
        self.opened = False
        self.contents = {}  # Will be populated when opened


class Dungeon:
    """Represents a procedurally generated dungeon."""
    
    def __init__(self, width: int = 50, height: int = 50, difficulty: int = 1, 
                 num_rooms: int = 10, min_room_size: int = 5, max_room_size: int = 10):
        """
        Initialize a dungeon.
        
        Args:
            width: Width of the dungeon in tiles
            height: Height of the dungeon in tiles
            difficulty: Difficulty level (affects enemies and rewards)
            num_rooms: Number of rooms to generate
            min_room_size: Minimum size of rooms
            max_room_size: Maximum size of rooms
        """
        self.width = max(width, 20)  # Ensure minimum width
        self.height = max(height, 20)  # Ensure minimum height
        self.difficulty = difficulty
        self.num_rooms = min(num_rooms, (width * height) // 100)  # Ensure reasonable number of rooms
        self.min_room_size = max(min_room_size, 3)  # Ensure minimum room size
        # Ensure max_room_size is at least equal to min_room_size
        self.max_room_size = max(self.min_room_size, min(max_room_size, min(width // 3, height // 3)))
        
        # Initialize the dungeon grid with walls
        self.grid: List[List[DungeonTile]] = [
            [DungeonTile(WALL_TILE, walkable=False) for _ in range(self.width)]
            for _ in range(self.height)
        ]
        
        # Lists to track rooms and entities
        self.rooms: List[DungeonRoom] = []
        self.enemies: List[Enemy] = []
        self.chests: List[Chest] = []
        
        # Generate the dungeon
        self._generate_dungeon()
    
    def _generate_dungeon(self) -> None:
        """Generate a procedural dungeon with rooms and corridors."""
        # Generate rooms
        attempts = 0
        max_attempts = 100
        
        while len(self.rooms) < self.num_rooms and attempts < max_attempts:
            # Generate random room dimensions
            width = random.randint(self.min_room_size, self.max_room_size)
            height = random.randint(self.min_room_size, self.max_room_size)
            
            # Ensure there's space for the room
            if self.width <= width + 2 or self.height <= height + 2:
                attempts += 1
                continue
            
            # Generate random position
            x = random.randint(1, self.width - width - 1)
            y = random.randint(1, self.height - height - 1)
            
            # Create a new room
            new_room = DungeonRoom(x, y, width, height)
            
            # Check if the room overlaps with any existing room
            overlaps = False
            for room in self.rooms:
                if new_room.overlaps(room):
                    overlaps = True
                    break
            
            if not overlaps:
                # Add the room to the list
                self.rooms.append(new_room)
                
                # Carve out the room in the grid
                for i in range(y, y + height):
                    for j in range(x, x + width):
                        self.grid[i][j] = DungeonTile(FLOOR_TILE)
            
            attempts += 1
        
        # If we couldn't generate enough rooms, adjust the number
        self.num_rooms = len(self.rooms)
        
        # If we have at least one room, proceed with the rest of generation
        if self.num_rooms > 0:
            # Connect rooms with corridors
            for i in range(len(self.rooms) - 1):
                self._create_corridor(self.rooms[i], self.rooms[i + 1])
            
            # Add special room types
            if len(self.rooms) >= 3:
                # Set the first room as the starting room
                self.rooms[0].room_type = "start"
                
                # Set the last room as the boss room
                self.rooms[-1].room_type = "boss"
                
                # Set a random room as a treasure room
                treasure_room_index = random.randint(1, len(self.rooms) - 2)
                self.rooms[treasure_room_index].room_type = "treasure"
            
            # Add enemies and chests
            self._add_enemies()
            self._add_chests()
    
    def _create_corridor(self, room1: DungeonRoom, room2: DungeonRoom) -> None:
        """Create a corridor between two rooms."""
        # Connect the rooms logically
        room1.connect_to(room2)
        
        # Get the center coordinates of both rooms
        x1, y1 = room1.center()
        x2, y2 = room2.center()
        
        # Randomly decide whether to go horizontal first or vertical first
        if random.random() < 0.5:
            # Horizontal first, then vertical
            self._create_horizontal_corridor(x1, x2, y1)
            self._create_vertical_corridor(y1, y2, x2)
        else:
            # Vertical first, then horizontal
            self._create_vertical_corridor(y1, y2, x1)
            self._create_horizontal_corridor(x1, x2, y2)
    
    def _create_horizontal_corridor(self, x1: int, x2: int, y: int) -> None:
        """Create a horizontal corridor from x1 to x2 at height y."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            # Check if we're at the edge of a room
            is_door = False
            for room in self.rooms:
                if ((x == room.x or x == room.x + room.width - 1) and 
                    room.y <= y < room.y + room.height):
                    is_door = True
                    break
            
            if is_door:
                self.grid[y][x] = DungeonTile(DOOR_TILE, walkable=True, interactable=True)
            else:
                self.grid[y][x] = DungeonTile(FLOOR_TILE)
    
    def _create_vertical_corridor(self, y1: int, y2: int, x: int) -> None:
        """Create a vertical corridor from y1 to y2 at position x."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            # Check if we're at the edge of a room
            is_door = False
            for room in self.rooms:
                if ((y == room.y or y == room.y + room.height - 1) and 
                    room.x <= x < room.x + room.width):
                    is_door = True
                    break
            
            if is_door:
                self.grid[y][x] = DungeonTile(DOOR_TILE, walkable=True, interactable=True)
            else:
                self.grid[y][x] = DungeonTile(FLOOR_TILE)
    
    def _add_enemies(self) -> None:
        """Add enemies to the dungeon."""
        # Add enemies to normal rooms
        for room in self.rooms:
            if room.room_type == "normal":
                # Add 1-3 enemies per normal room
                num_enemies = random.randint(1, 3)
                for _ in range(num_enemies):
                    # Find a valid position in the room
                    x = random.randint(room.x + 1, room.x + room.width - 2)
                    y = random.randint(room.y + 1, room.y + room.height - 2)
                    
                    # Create an enemy
                    enemy_type = random.choice(["pawn", "knight", "bishop", "rook"])
                    enemy = Enemy((x, y), enemy_type, self.difficulty)
                    self.enemies.append(enemy)
                    
                    # Place the enemy on the grid
                    self.grid[y][x].entity = enemy
                    self.grid[y][x].interactable = True
            
            elif room.room_type == "boss":
                # Add a boss enemy
                x, y = room.center()
                boss = Enemy((x, y), "queen", self.difficulty + 2)
                self.enemies.append(boss)
                
                # Place the boss on the grid
                self.grid[y][x].entity = boss
                self.grid[y][x].interactable = True
    
    def _add_chests(self) -> None:
        """Add treasure chests to the dungeon."""
        # Add a chest to the treasure room
        for room in self.rooms:
            if room.room_type == "treasure":
                # Add 2-3 chests to the treasure room
                num_chests = random.randint(2, 3)
                for _ in range(num_chests):
                    # Find a valid position in the room
                    x = random.randint(room.x + 1, room.x + room.width - 2)
                    y = random.randint(room.y + 1, room.y + room.height - 2)
                    
                    # Create a chest
                    chest_type = random.choice(["normal", "rare"])
                    chest = Chest((x, y), chest_type)
                    self.chests.append(chest)
                    
                    # Place the chest on the grid
                    self.grid[y][x].entity = chest
                    self.grid[y][x].interactable = True
            
            elif room.room_type == "normal" and random.random() < 0.3:
                # 30% chance to add a chest to a normal room
                x = random.randint(room.x + 1, room.x + room.width - 2)
                y = random.randint(room.y + 1, room.y + room.height - 2)
                
                # Create a chest
                chest = Chest((x, y), "normal")
                self.chests.append(chest)
                
                # Place the chest on the grid
                self.grid[y][x].entity = chest
                self.grid[y][x].interactable = True
    
    def get_starting_position(self) -> Tuple[int, int]:
        """Get the starting position for the player."""
        for room in self.rooms:
            if room.room_type == "start":
                return room.center()
        
        # Fallback to the first room if no start room is found
        if self.rooms:
            return self.rooms[0].center()
        
        # Fallback to the center of the dungeon if no rooms exist
        return (self.width // 2, self.height // 2)
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a position is walkable."""
        # Check if the position is within bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Check if the tile is walkable
        return self.grid[y][x].walkable and self.grid[y][x].entity is None
    
    def get_entity_at(self, x: int, y: int) -> Optional[Any]:
        """Get the entity at a position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x].entity
        return None
    
    def update_visibility(self, player_x: int, player_y: int, vision_range: int = 5) -> None:
        """Update which tiles are visible to the player."""
        # Reset visibility
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].visible = False
        
        # Mark tiles within vision range as visible
        for y in range(max(0, player_y - vision_range), min(self.height, player_y + vision_range + 1)):
            for x in range(max(0, player_x - vision_range), min(self.width, player_x + vision_range + 1)):
                # Calculate distance
                distance = ((x - player_x) ** 2 + (y - player_y) ** 2) ** 0.5
                
                if distance <= vision_range:
                    # Check if there's a clear line of sight
                    if self._has_line_of_sight(player_x, player_y, x, y):
                        self.grid[y][x].visible = True
                        self.grid[y][x].discovered = True
    
    def _has_line_of_sight(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if there's a clear line of sight between two points."""
        # Bresenham's line algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while x1 != x2 or y1 != y2:
            # Check if the current tile blocks vision
            if (x1 != x2 or y1 != y2) and self.grid[y1][x1].tile_type == WALL_TILE:
                return False
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        
        return True 