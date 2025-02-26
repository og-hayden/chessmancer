import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.dungeon import Dungeon

# Create a dungeon
dungeon = Dungeon(width=30, height=30, num_rooms=5)

# Print some information about the dungeon
print(f"Dungeon size: {dungeon.width}x{dungeon.height}")
print(f"Number of rooms: {len(dungeon.rooms)}")
print(f"Number of enemies: {len(dungeon.enemies)}")
print(f"Number of chests: {len(dungeon.chests)}")

# Check the starting position
start_x, start_y = dungeon.get_starting_position()
print(f"Starting position: ({start_x}, {start_y})")

# Check if the starting position is walkable
is_walkable = dungeon.is_walkable(start_x, start_y)
print(f"Is starting position walkable: {is_walkable}")

print("Test completed successfully!") 