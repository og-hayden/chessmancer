import os
import pygame
import random
from typing import Tuple

# Enable GPU acceleration if available
os.environ['PYGAME_HWSURFACE'] = '1'
os.environ['PYGAME_DOUBLEBUF'] = '1'

# Game modes
MODE_CHESS = 0
MODE_DUNGEON = 1

# Board constants
BOARD_SIZE = 8
SQUARE_SIZE = 80
BOARD_PX = BOARD_SIZE * SQUARE_SIZE
WINDOW_WIDTH = BOARD_PX + 250  # Increased UI panel width
WINDOW_HEIGHT = BOARD_PX
FPS = 60

# Dungeon constants
TILE_SIZE = 40
FLOOR_TILE = "floor"
WALL_TILE = "wall"
DOOR_TILE = "door"
ENEMY_TILE = "enemy"
CHEST_TILE = "chest"
PLAYER_TILE = "player"

# Animation constants
ANIMATION_SPEED = 12  # Pixels per frame
MIN_AI_MOVE_TIME = 1.0  # Minimum time in seconds for AI to "think"
MAX_AI_MOVE_TIME = 3.0  # Maximum time in seconds for AI to "think"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)  # Light brown
DARK_SQUARE = (181, 136, 99)    # Dark brown
BOARD_BORDER = (120, 80, 50)    # Dark wood color
HIGHLIGHT = (124, 252, 0, 150)  # Semi-transparent green
SELECTED = (255, 215, 0, 180)   # Semi-transparent gold
LAST_MOVE = (100, 149, 237, 120)  # Semi-transparent cornflower blue
WHITE_PIECE = (245, 245, 245)
BLACK_PIECE = (40, 40, 40)
UI_BG = (45, 45, 65)
UI_PANEL_BORDER = (60, 60, 85)
UI_TEXT = (230, 230, 230)
UI_HEADING = (255, 255, 255)
UI_BUTTON = (80, 100, 140)
UI_BUTTON_HOVER = (100, 120, 180)
UI_BUTTON_ACTIVE = (120, 140, 200)
UI_BUTTON_TEXT = (240, 240, 240)
UI_SECTION_BG = (55, 55, 75)

# Piece types
PAWN = 'pawn'
KNIGHT = 'knight'
BISHOP = 'bishop'
ROOK = 'rook'
QUEEN = 'queen'
KING = 'king'

# Game modes
MODE_HUMAN_VS_HUMAN = 0
MODE_HUMAN_VS_AI = 1

# Initialize pygame
pygame.init()

# Set up the display with hardware acceleration if available
flags = pygame.HWSURFACE | pygame.DOUBLEBUF
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
pygame.display.set_caption("Chessmancer")

def create_piece_images() -> dict:
    """Load chess piece images from PNG files and return them in a dictionary."""
    pieces = {}
    piece_types = [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]
    colors = ['white', 'black']
    
    for color in colors:
        for piece_type in piece_types:
            # Construct the filename
            filename = f"pieces/{color}-{piece_type}.png"
            
            # Load the image
            original_image = pygame.image.load(filename).convert_alpha()
            
            # Scale the image to fit the square size
            scaled_image = pygame.transform.scale(original_image, (SQUARE_SIZE, SQUARE_SIZE))
            
            # Add a subtle drop shadow
            shadow = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            shadow_offset = 3
            
            # Create a copy of the scaled image for shadow creation
            temp_image = scaled_image.copy()
            
            # Create shadow by offsetting a darkened copy of the image
            for y in range(SQUARE_SIZE):
                for x in range(SQUARE_SIZE):
                    if x < SQUARE_SIZE - shadow_offset and y < SQUARE_SIZE - shadow_offset:
                        pixel_color = temp_image.get_at((x, y))
                        if pixel_color[3] > 50:  # If pixel is not too transparent
                            shadow_x = min(x + shadow_offset, SQUARE_SIZE - 1)
                            shadow_y = min(y + shadow_offset, SQUARE_SIZE - 1)
                            shadow.set_at((shadow_x, shadow_y), (0, 0, 0, 50))  # Semi-transparent black
            
            # Create final image with shadow
            final_image = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            final_image.blit(shadow, (0, 0))
            final_image.blit(scaled_image, (0, 0))
            
            pieces[f'{color}_{piece_type}'] = final_image
    
    return pieces

def create_tile_images() -> dict:
    """Create images for dungeon tiles."""
    tiles = {}
    
    # Floor tile (light gray)
    floor = pygame.Surface((TILE_SIZE, TILE_SIZE))
    floor.fill((180, 180, 180))
    # Add some texture
    for i in range(5):
        x = random.randint(0, TILE_SIZE - 3)
        y = random.randint(0, TILE_SIZE - 3)
        pygame.draw.rect(floor, (160, 160, 160), pygame.Rect(x, y, 3, 3))
    tiles[FLOOR_TILE] = floor
    
    # Wall tile (dark gray with texture)
    wall = pygame.Surface((TILE_SIZE, TILE_SIZE))
    wall.fill((100, 100, 100))
    # Add brick pattern
    for y in range(0, TILE_SIZE, 10):
        offset = 0 if y % 20 == 0 else 10
        for x in range(offset, TILE_SIZE, 20):
            brick = pygame.Rect(x, y, 18, 8)
            pygame.draw.rect(wall, (120, 120, 120), brick)
            pygame.draw.rect(wall, (80, 80, 80), brick, 1)
    tiles[WALL_TILE] = wall
    
    # Door tile (brown)
    door = pygame.Surface((TILE_SIZE, TILE_SIZE))
    door.fill((150, 100, 50))
    # Add door details
    pygame.draw.rect(door, (120, 80, 40), pygame.Rect(5, 5, TILE_SIZE - 10, TILE_SIZE - 10))
    pygame.draw.circle(door, (200, 200, 0), (TILE_SIZE - 10, TILE_SIZE // 2), 3)  # Doorknob
    tiles[DOOR_TILE] = door
    
    # Enemy tile (red figure)
    enemy = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    enemy.fill((0, 0, 0, 0))  # Transparent
    # Draw a simple enemy figure
    pygame.draw.circle(enemy, (200, 50, 50), (TILE_SIZE // 2, TILE_SIZE // 3), TILE_SIZE // 4)  # Head
    pygame.draw.rect(enemy, (200, 50, 50), pygame.Rect(TILE_SIZE // 3, TILE_SIZE // 2, TILE_SIZE // 3, TILE_SIZE // 3))  # Body
    tiles[ENEMY_TILE] = enemy
    
    # Chest tile (gold chest)
    chest = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    chest.fill((0, 0, 0, 0))  # Transparent
    # Draw a simple chest
    pygame.draw.rect(chest, (150, 100, 50), pygame.Rect(5, TILE_SIZE // 2, TILE_SIZE - 10, TILE_SIZE // 3))  # Chest base
    pygame.draw.rect(chest, (200, 150, 50), pygame.Rect(5, TILE_SIZE // 2 - 5, TILE_SIZE - 10, 10))  # Chest lid
    pygame.draw.rect(chest, (200, 200, 0), pygame.Rect(TILE_SIZE // 2 - 3, TILE_SIZE // 2, 6, 5))  # Lock
    tiles[CHEST_TILE] = chest
    
    # Player tile (blue figure)
    player = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    player.fill((0, 0, 0, 0))  # Transparent
    # Draw a simple player figure
    pygame.draw.circle(player, (50, 100, 200), (TILE_SIZE // 2, TILE_SIZE // 3), TILE_SIZE // 4)  # Head
    pygame.draw.rect(player, (50, 100, 200), pygame.Rect(TILE_SIZE // 3, TILE_SIZE // 2, TILE_SIZE // 3, TILE_SIZE // 3))  # Body
    tiles[PLAYER_TILE] = player
    
    return tiles 