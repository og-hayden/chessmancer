import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Importing Dungeon class...")
from models.dungeon import Dungeon
print("Import successful!")

print("Creating Dungeon instance...")
dungeon = Dungeon(width=10, height=10, num_rooms=3)
print("Dungeon created successfully!") 