import os
import pygame
from typing import Tuple

# Enable GPU acceleration if available
os.environ['PYGAME_HWSURFACE'] = '1'
os.environ['PYGAME_DOUBLEBUF'] = '1'

# Board constants
BOARD_SIZE = 8
SQUARE_SIZE = 80
BOARD_PX = BOARD_SIZE * SQUARE_SIZE
WINDOW_WIDTH = BOARD_PX + 250  # Increased UI panel width
WINDOW_HEIGHT = BOARD_PX
FPS = 60

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