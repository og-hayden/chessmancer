import pygame
import numpy as np
import os
import time
import math
from typing import List, Tuple, Dict, Optional, Set
from chess_ai import ChessAI

# Enable GPU acceleration if available
os.environ['PYGAME_HWSURFACE'] = '1'
os.environ['PYGAME_DOUBLEBUF'] = '1'

# Constants
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

# Create piece images using shapes
def create_piece_images() -> Dict[str, pygame.Surface]:
    """Create visually appealing chess piece images using shapes and return them in a dictionary."""
    pieces = {}
    piece_types = [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]
    colors = ['white', 'black']
    
    for color in colors:
        for piece_type in piece_types:
            # Create a transparent surface
            image = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            
            # Set the piece color
            piece_color = WHITE_PIECE if color == 'white' else BLACK_PIECE
            outline_color = BLACK if color == 'white' else WHITE
            highlight_color = tuple(min(c + 40, 255) for c in piece_color)
            shadow_color = tuple(max(c - 40, 0) for c in piece_color)
            
            # Common base for all pieces
            def draw_piece_base():
                # Draw base shadow
                base_shadow = pygame.Rect(
                    SQUARE_SIZE // 4 - 2, 
                    SQUARE_SIZE * 2 // 3 + 2, 
                    SQUARE_SIZE // 2 + 4, 
                    SQUARE_SIZE // 5 + 2
                )
                pygame.draw.ellipse(image, shadow_color, base_shadow)
                
                # Draw base
                base = pygame.Rect(
                    SQUARE_SIZE // 4, 
                    SQUARE_SIZE * 2 // 3, 
                    SQUARE_SIZE // 2, 
                    SQUARE_SIZE // 5
                )
                pygame.draw.ellipse(image, piece_color, base)
                
                # Draw base highlight
                pygame.draw.ellipse(image, highlight_color, base, 2)
                
                # Draw base outline
                pygame.draw.ellipse(image, outline_color, base, 1)
            
            # Draw the piece based on its type
            if piece_type == PAWN:
                # Draw a more detailed pawn
                # Head
                pygame.draw.circle(
                    image, 
                    piece_color, 
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 2 - 5), 
                    SQUARE_SIZE // 5
                )
                pygame.draw.circle(
                    image, 
                    highlight_color, 
                    (SQUARE_SIZE // 2 - 3, SQUARE_SIZE // 2 - 8), 
                    SQUARE_SIZE // 12
                )
                pygame.draw.circle(
                    image, 
                    outline_color, 
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 2 - 5), 
                    SQUARE_SIZE // 5, 
                    1
                )
                
                # Body
                body_points = [
                    (SQUARE_SIZE // 2 - SQUARE_SIZE // 6, SQUARE_SIZE // 2 + 5),
                    (SQUARE_SIZE // 2 + SQUARE_SIZE // 6, SQUARE_SIZE // 2 + 5),
                    (SQUARE_SIZE // 2 + SQUARE_SIZE // 5, SQUARE_SIZE * 2 // 3),
                    (SQUARE_SIZE // 2 - SQUARE_SIZE // 5, SQUARE_SIZE * 2 // 3)
                ]
                pygame.draw.polygon(image, piece_color, body_points)
                pygame.draw.polygon(image, outline_color, body_points, 1)
                
                # Add collar detail
                collar_rect = pygame.Rect(
                    SQUARE_SIZE // 2 - SQUARE_SIZE // 8, 
                    SQUARE_SIZE // 2 + 2, 
                    SQUARE_SIZE // 4, 
                    SQUARE_SIZE // 16
                )
                pygame.draw.rect(image, highlight_color, collar_rect)
                pygame.draw.rect(image, outline_color, collar_rect, 1)
                
                draw_piece_base()
            
            elif piece_type == KNIGHT:
                # Draw a more detailed knight (horse head)
                # Neck
                neck_points = [
                    (SQUARE_SIZE // 2 - 10, SQUARE_SIZE // 2 + 15),
                    (SQUARE_SIZE // 2 - 5, SQUARE_SIZE // 2 - 5),
                    (SQUARE_SIZE // 2 + 5, SQUARE_SIZE // 2 - 5),
                    (SQUARE_SIZE // 2 + 10, SQUARE_SIZE // 2 + 15)
                ]
                pygame.draw.polygon(image, piece_color, neck_points)
                pygame.draw.polygon(image, outline_color, neck_points, 1)
                
                # Head
                head_points = [
                    (SQUARE_SIZE // 2 - 5, SQUARE_SIZE // 2 - 5),
                    (SQUARE_SIZE // 2 - 12, SQUARE_SIZE // 2 - 15),
                    (SQUARE_SIZE // 2 - 5, SQUARE_SIZE // 2 - 20),
                    (SQUARE_SIZE // 2 + 5, SQUARE_SIZE // 2 - 20),
                    (SQUARE_SIZE // 2 + 15, SQUARE_SIZE // 2 - 10),
                    (SQUARE_SIZE // 2 + 5, SQUARE_SIZE // 2 - 5)
                ]
                pygame.draw.polygon(image, piece_color, head_points)
                pygame.draw.polygon(image, outline_color, head_points, 1)
                
                # Mane
                mane_points = [
                    (SQUARE_SIZE // 2 - 5, SQUARE_SIZE // 2 - 5),
                    (SQUARE_SIZE // 2 - 10, SQUARE_SIZE // 2 - 10),
                    (SQUARE_SIZE // 2 - 8, SQUARE_SIZE // 2),
                    (SQUARE_SIZE // 2 - 6, SQUARE_SIZE // 2 + 10)
                ]
                pygame.draw.polygon(image, highlight_color, mane_points)
                pygame.draw.polygon(image, outline_color, mane_points, 1)
                
                # Eye
                pygame.draw.circle(
                    image, 
                    outline_color, 
                    (SQUARE_SIZE // 2 + 5, SQUARE_SIZE // 2 - 15), 
                    2
                )
                
                # Ear
                ear_points = [
                    (SQUARE_SIZE // 2 - 5, SQUARE_SIZE // 2 - 20),
                    (SQUARE_SIZE // 2 - 8, SQUARE_SIZE // 2 - 25),
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 2 - 25),
                    (SQUARE_SIZE // 2 + 5, SQUARE_SIZE // 2 - 20)
                ]
                pygame.draw.polygon(image, piece_color, ear_points)
                pygame.draw.polygon(image, outline_color, ear_points, 1)
                
                draw_piece_base()
            
            elif piece_type == BISHOP:
                # Draw a more detailed bishop
                # Main body
                pygame.draw.ellipse(
                    image, 
                    piece_color, 
                    (SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 2)
                )
                pygame.draw.ellipse(
                    image, 
                    outline_color, 
                    (SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 2), 
                    1
                )
                
                # Head
                pygame.draw.circle(
                    image, 
                    piece_color, 
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 3), 
                    SQUARE_SIZE // 8
                )
                pygame.draw.circle(
                    image, 
                    outline_color, 
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 3), 
                    SQUARE_SIZE // 8, 
                    1
                )
                
                # Cross
                pygame.draw.line(
                    image, 
                    outline_color,
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 5),
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 3 - 2), 
                    2
                )
                pygame.draw.line(
                    image, 
                    outline_color,
                    (SQUARE_SIZE // 2 - 5, SQUARE_SIZE // 4),
                    (SQUARE_SIZE // 2 + 5, SQUARE_SIZE // 4), 
                    2
                )
                
                # Collar detail
                pygame.draw.line(
                    image, 
                    highlight_color,
                    (SQUARE_SIZE // 3 + 2, SQUARE_SIZE // 2),
                    (SQUARE_SIZE * 2 // 3 - 2, SQUARE_SIZE // 2), 
                    3
                )
                
                draw_piece_base()
            
            elif piece_type == ROOK:
                # Draw a more detailed rook (castle tower)
                # Main body
                tower_rect = pygame.Rect(
                    SQUARE_SIZE // 3, 
                    SQUARE_SIZE // 3, 
                    SQUARE_SIZE // 3, 
                    SQUARE_SIZE // 2
                )
                pygame.draw.rect(image, piece_color, tower_rect)
                pygame.draw.rect(image, outline_color, tower_rect, 1)
                
                # Crenellations (castle top)
                crenel_width = SQUARE_SIZE // 9
                for i in range(3):
                    x = SQUARE_SIZE // 3 + (i * crenel_width)
                    crenel_rect = pygame.Rect(
                        x, 
                        SQUARE_SIZE // 4, 
                        crenel_width, 
                        SQUARE_SIZE // 12
                    )
                    pygame.draw.rect(image, piece_color, crenel_rect)
                    pygame.draw.rect(image, outline_color, crenel_rect, 1)
                
                # Window
                window_rect = pygame.Rect(
                    SQUARE_SIZE // 2 - SQUARE_SIZE // 12, 
                    SQUARE_SIZE // 2 - SQUARE_SIZE // 12, 
                    SQUARE_SIZE // 6, 
                    SQUARE_SIZE // 6
                )
                pygame.draw.rect(image, shadow_color, window_rect)
                pygame.draw.rect(image, outline_color, window_rect, 1)
                
                # Highlight on top
                pygame.draw.line(
                    image, 
                    highlight_color,
                    (SQUARE_SIZE // 3, SQUARE_SIZE // 3),
                    (SQUARE_SIZE * 2 // 3, SQUARE_SIZE // 3), 
                    2
                )
                
                draw_piece_base()
            
            elif piece_type == QUEEN:
                # Draw a more detailed queen
                # Main body
                pygame.draw.ellipse(
                    image, 
                    piece_color, 
                    (SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 2)
                )
                pygame.draw.ellipse(
                    image, 
                    outline_color, 
                    (SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 2), 
                    1
                )
                
                # Crown
                crown_points = [
                    (SQUARE_SIZE // 3, SQUARE_SIZE // 3),
                    (SQUARE_SIZE // 3 + SQUARE_SIZE // 15, SQUARE_SIZE // 4),
                    (SQUARE_SIZE // 2 - SQUARE_SIZE // 10, SQUARE_SIZE // 3 - SQUARE_SIZE // 15),
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 5),
                    (SQUARE_SIZE // 2 + SQUARE_SIZE // 10, SQUARE_SIZE // 3 - SQUARE_SIZE // 15),
                    (SQUARE_SIZE * 2 // 3 - SQUARE_SIZE // 15, SQUARE_SIZE // 4),
                    (SQUARE_SIZE * 2 // 3, SQUARE_SIZE // 3)
                ]
                pygame.draw.polygon(image, piece_color, crown_points)
                pygame.draw.polygon(image, outline_color, crown_points, 1)
                
                # Jewels on crown
                jewel_positions = [
                    (SQUARE_SIZE // 3 + SQUARE_SIZE // 15, SQUARE_SIZE // 4),
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 5),
                    (SQUARE_SIZE * 2 // 3 - SQUARE_SIZE // 15, SQUARE_SIZE // 4)
                ]
                for pos in jewel_positions:
                    pygame.draw.circle(image, highlight_color, pos, 3)
                    pygame.draw.circle(image, outline_color, pos, 3, 1)
                
                # Collar detail
                pygame.draw.line(
                    image, 
                    highlight_color,
                    (SQUARE_SIZE // 3 + 2, SQUARE_SIZE // 2),
                    (SQUARE_SIZE * 2 // 3 - 2, SQUARE_SIZE // 2), 
                    3
                )
                
                draw_piece_base()
            
            elif piece_type == KING:
                # Draw a more detailed king
                # Main body
                pygame.draw.ellipse(
                    image, 
                    piece_color, 
                    (SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 2)
                )
                pygame.draw.ellipse(
                    image, 
                    outline_color, 
                    (SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 3, SQUARE_SIZE // 2), 
                    1
                )
                
                # Crown base
                crown_rect = pygame.Rect(
                    SQUARE_SIZE // 3, 
                    SQUARE_SIZE // 4, 
                    SQUARE_SIZE // 3, 
                    SQUARE_SIZE // 12
                )
                pygame.draw.rect(image, piece_color, crown_rect)
                pygame.draw.rect(image, outline_color, crown_rect, 1)
                
                # Crown points
                point_width = SQUARE_SIZE // 15
                for i in range(3):
                    x = SQUARE_SIZE // 3 + (i * point_width * 2) + point_width // 2
                    point_points = [
                        (x - point_width // 2, SQUARE_SIZE // 4),
                        (x, SQUARE_SIZE // 6),
                        (x + point_width // 2, SQUARE_SIZE // 4)
                    ]
                    pygame.draw.polygon(image, piece_color, point_points)
                    pygame.draw.polygon(image, outline_color, point_points, 1)
                
                # Cross on top
                pygame.draw.line(
                    image, 
                    outline_color,
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 8),
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 4), 
                    2
                )
                pygame.draw.line(
                    image, 
                    outline_color,
                    (SQUARE_SIZE // 2 - 5, SQUARE_SIZE // 6),
                    (SQUARE_SIZE // 2 + 5, SQUARE_SIZE // 6), 
                    2
                )
                
                # Collar detail
                pygame.draw.line(
                    image, 
                    highlight_color,
                    (SQUARE_SIZE // 3 + 2, SQUARE_SIZE // 2),
                    (SQUARE_SIZE * 2 // 3 - 2, SQUARE_SIZE // 2), 
                    3
                )
                
                draw_piece_base()
            
            # Apply anti-aliasing effect by scaling down and up
            temp_surface = pygame.Surface((SQUARE_SIZE * 2, SQUARE_SIZE * 2), pygame.SRCALPHA)
            pygame.transform.scale(image, (SQUARE_SIZE * 2, SQUARE_SIZE * 2), temp_surface)
            pygame.transform.scale(temp_surface, (SQUARE_SIZE, SQUARE_SIZE), image)
            
            # Add a subtle drop shadow
            shadow = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            shadow_offset = 3
            for y in range(SQUARE_SIZE):
                for x in range(SQUARE_SIZE):
                    if image.get_at((x, y))[3] > 0:  # If pixel is not fully transparent
                        shadow_x = min(x + shadow_offset, SQUARE_SIZE - 1)
                        shadow_y = min(y + shadow_offset, SQUARE_SIZE - 1)
                        shadow.set_at((shadow_x, shadow_y), (0, 0, 0, 50))  # Semi-transparent black
            
            # Create final image with shadow
            final_image = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            final_image.blit(shadow, (0, 0))
            final_image.blit(image, (0, 0))
            
            pieces[f'{color}_{piece_type}'] = final_image
    
    return pieces

class Button:
    """A modern button class for the UI."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int] = UI_BUTTON, 
                 hover_color: Tuple[int, int, int] = UI_BUTTON_HOVER,
                 active_color: Tuple[int, int, int] = UI_BUTTON_ACTIVE,
                 text_color: Tuple[int, int, int] = UI_BUTTON_TEXT,
                 icon: Optional[pygame.Surface] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.active_color = active_color
        self.text_color = text_color
        self.hovered = False
        self.active = False
        self.icon = icon
        self.font = pygame.font.SysFont('Arial', 16)
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button on the screen with a modern look."""
        # Determine button color based on state
        if self.active:
            color = self.active_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.color
            
        # Draw button with rounded corners
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # Add a subtle gradient effect
        gradient_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height // 2)
        gradient_color = tuple(min(c + 20, 255) for c in color)
        pygame.draw.rect(screen, gradient_color, gradient_rect, border_radius=8)
        
        # Add a subtle border
        border_color = tuple(max(c - 30, 0) for c in color)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)
        
        # Draw icon if provided
        text_x_offset = 0
        if self.icon:
            icon_rect = self.icon.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
            screen.blit(self.icon, icon_rect)
            text_x_offset = self.icon.get_width() + 5
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        if self.icon:
            text_rect = text_surface.get_rect(midleft=(self.rect.x + 15 + text_x_offset, self.rect.centery))
        else:
            text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Add a subtle shadow effect for text
        shadow_surface = self.font.render(self.text, True, (0, 0, 0, 128))
        shadow_rect = shadow_surface.get_rect(topleft=(text_rect.x + 1, text_rect.y + 1))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)
        
        # Add a subtle highlight when hovered
        if self.hovered:
            highlight_surface = pygame.Surface((self.rect.width, 2), pygame.SRCALPHA)
            highlight_surface.fill((255, 255, 255, 100))
            screen.blit(highlight_surface, (self.rect.x, self.rect.y))
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update the button state based on mouse position."""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> bool:
        """Check if the button is clicked and update active state."""
        was_clicked = self.rect.collidepoint(mouse_pos) and mouse_clicked
        if was_clicked:
            self.active = True
        return was_clicked
        
    def set_active(self, active: bool) -> None:
        """Set the active state of the button."""
        self.active = active

class AnimatedPiece:
    """Represents a chess piece that is being animated."""
    
    def __init__(self, piece_type: str, color: str, 
                 start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                 image: pygame.Surface):
        self.piece_type = piece_type
        self.color = color
        
        # Convert board positions to pixel positions
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        self.start_x = start_col * SQUARE_SIZE
        self.start_y = start_row * SQUARE_SIZE
        self.end_x = end_col * SQUARE_SIZE
        self.end_y = end_row * SQUARE_SIZE
        
        self.current_x = float(self.start_x)
        self.current_y = float(self.start_y)
        
        self.image = image
        self.completed = False
        
        # Calculate the distance and direction
        self.dx = self.end_x - self.start_x
        self.dy = self.end_y - self.start_y
        self.distance = math.sqrt(self.dx**2 + self.dy**2)
        
        # Normalize direction vector
        if self.distance > 0:
            self.dx /= self.distance
            self.dy /= self.distance
    
    def update(self) -> None:
        """Update the position of the animated piece."""
        if self.completed:
            return
            
        # Calculate how much to move this frame
        move_amount = ANIMATION_SPEED
        
        # Calculate the distance left to move
        remaining_distance = math.sqrt(
            (self.end_x - self.current_x)**2 + 
            (self.end_y - self.current_y)**2
        )
        
        # If we're close enough to the end, snap to it
        if remaining_distance <= move_amount:
            self.current_x = self.end_x
            self.current_y = self.end_y
            self.completed = True
        else:
            # Move along the direction vector
            self.current_x += self.dx * move_amount
            self.current_y += self.dy * move_amount
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the animated piece at its current position."""
        screen.blit(self.image, (int(self.current_x), int(self.current_y)))
    
    def is_completed(self) -> bool:
        """Check if the animation is completed."""
        return self.completed

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

class ChessBoard:
    """Represents the chess board and game state."""
    
    def __init__(self, game_mode: int = MODE_HUMAN_VS_HUMAN, ai_difficulty: int = 10):
        self.board: List[List[Optional[ChessPiece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected_piece: Optional[ChessPiece] = None
        self.legal_moves: List[Tuple[int, int]] = []
        self.turn = 'white'
        self.game_mode = game_mode
        self.ai_difficulty = ai_difficulty
        self.ai = ChessAI(difficulty=ai_difficulty) if game_mode == MODE_HUMAN_VS_AI else None
        self.move_history: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
        self.game_over = False
        self.game_result = ""
        self.thinking = False
        self.last_pawn_double_move: Optional[Tuple[int, int]] = None  # Position of pawn that just moved two squares
        
        # Animation properties
        self.animated_pieces: List[AnimatedPiece] = []
        self.animating = False
        self.pending_ai_move = False
        self.ai_move_start_time = 0
        self.ai_move_duration = 0
        
        self.setup_pieces()
        
    def setup_pieces(self) -> None:
        """Set up the initial position of all pieces on the board."""
        # Set up pawns
        for col in range(BOARD_SIZE):
            self.board[1][col] = ChessPiece(PAWN, 'black', (1, col))
            self.board[6][col] = ChessPiece(PAWN, 'white', (6, col))
        
        # Set up other pieces
        back_row_pieces = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
        
        for col, piece_type in enumerate(back_row_pieces):
            self.board[0][col] = ChessPiece(piece_type, 'black', (0, col))
            self.board[7][col] = ChessPiece(piece_type, 'white', (7, col))
    
    def draw(self, screen: pygame.Surface, piece_images: Dict[str, pygame.Surface]) -> None:
        """Draw the chess board and pieces with a modern look."""
        # Draw a border around the board
        border_width = 10
        pygame.draw.rect(
            screen, 
            BOARD_BORDER, 
            (-border_width, -border_width, BOARD_PX + border_width * 2, BOARD_PX + border_width * 2)
        )
        
        # Draw the board squares
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(
                    screen, 
                    color, 
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                )
                
                # Draw coordinates on the edge squares
                if row == BOARD_SIZE - 1 or col == 0:
                    coord_font = pygame.font.SysFont('Arial', 12)
                    
                    if row == BOARD_SIZE - 1:
                        # Draw column letters (a-h)
                        letter = chr(97 + col)  # ASCII 'a' starts at 97
                        text = coord_font.render(letter, True, DARK_SQUARE if (row + col) % 2 == 0 else LIGHT_SQUARE)
                        text_rect = text.get_rect(bottomright=(
                            (col + 1) * SQUARE_SIZE - 3, 
                            (row + 1) * SQUARE_SIZE - 3
                        ))
                        screen.blit(text, text_rect)
                    
                    if col == 0:
                        # Draw row numbers (1-8)
                        number = str(BOARD_SIZE - row)
                        text = coord_font.render(number, True, DARK_SQUARE if (row + col) % 2 == 0 else LIGHT_SQUARE)
                        text_rect = text.get_rect(topleft=(3, row * SQUARE_SIZE + 3))
                        screen.blit(text, text_rect)
        
        # Draw highlights for the last move
        if self.move_history:
            last_move = self.move_history[-1]
            from_pos, to_pos = last_move
            
            for pos in [from_pos, to_pos]:
                row, col = pos
                last_move_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(last_move_surface, LAST_MOVE, (0, 0, SQUARE_SIZE, SQUARE_SIZE))
                screen.blit(last_move_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
        
        # Draw highlights for legal moves
        for row, col in self.legal_moves:
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            
            # If the square is empty, draw a circle, otherwise draw a rectangle
            if self.board[row][col] is None:
                # Draw a circle for empty squares
                pygame.draw.circle(
                    highlight_surface, 
                    HIGHLIGHT, 
                    (SQUARE_SIZE // 2, SQUARE_SIZE // 2), 
                    SQUARE_SIZE // 6
                )
            else:
                # Draw a rectangle for captures
                pygame.draw.rect(highlight_surface, HIGHLIGHT, (0, 0, SQUARE_SIZE, SQUARE_SIZE))
            
            screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
        
        # Draw highlight for selected piece
        if self.selected_piece:
            row, col = self.selected_piece.position
            selected_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(selected_surface, SELECTED, (0, 0, SQUARE_SIZE, SQUARE_SIZE))
            screen.blit(selected_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
        
        # Draw the pieces (except those being animated)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    # Skip drawing pieces that are being animated
                    if self.animating and self._is_piece_animating(row, col):
                        continue
                    
                    image = piece_images[piece.get_image_key()]
                    screen.blit(image, (col * SQUARE_SIZE, row * SQUARE_SIZE))
        
        # Draw animated pieces
        for animated_piece in self.animated_pieces:
            animated_piece.draw(screen)
        
        # Draw the UI panel
        self.draw_ui(screen)
    
    def _is_piece_animating(self, row: int, col: int) -> bool:
        """Check if a piece at the given position is currently being animated."""
        # If we're not animating, no piece is animating
        if not self.animating:
            return False
            
        # Check if this position is the end position of any animated piece
        for animated_piece in self.animated_pieces:
            end_col = int(animated_piece.end_x / SQUARE_SIZE)
            end_row = int(animated_piece.end_y / SQUARE_SIZE)
            
            if row == end_row and col == end_col:
                return True
                
        return False
    
    def update_animations(self) -> None:
        """Update all animated pieces and check if animations are complete."""
        if not self.animating:
            return
            
        # Update all animated pieces
        all_completed = True
        for animated_piece in self.animated_pieces:
            animated_piece.update()
            if not animated_piece.is_completed():
                all_completed = False
        
        # If all animations are complete, clear the list and update the game state
        if all_completed:
            self.animated_pieces = []
            self.animating = False
            
            # If there's a pending AI move, start the AI thinking process
            if self.pending_ai_move:
                self.thinking = True
                self.pending_ai_move = False
                self.ai_move_start_time = time.time()
                # Set a random thinking time between MIN and MAX
                self.ai_move_duration = MIN_AI_MOVE_TIME + (MAX_AI_MOVE_TIME - MIN_AI_MOVE_TIME) * np.random.random()
    
    def draw_ui(self, screen: pygame.Surface) -> None:
        """Draw a modern UI panel on the right side of the board."""
        # Draw the UI background with a border
        pygame.draw.rect(screen, UI_PANEL_BORDER, (BOARD_PX - 2, -2, WINDOW_WIDTH - BOARD_PX + 4, WINDOW_HEIGHT + 4))
        pygame.draw.rect(screen, UI_BG, (BOARD_PX, 0, WINDOW_WIDTH - BOARD_PX, WINDOW_HEIGHT))
        
        # Draw a title/header
        title_font = pygame.font.SysFont('Arial', 24, bold=True)
        title_text = "CHESSMANCER"
        title_surface = title_font.render(title_text, True, UI_HEADING)
        title_rect = title_surface.get_rect(midtop=(BOARD_PX + (WINDOW_WIDTH - BOARD_PX) // 2, 20))
        screen.blit(title_surface, title_rect)
        
        # Draw a separator line
        pygame.draw.line(
            screen, 
            UI_PANEL_BORDER, 
            (BOARD_PX + 20, title_rect.bottom + 15), 
            (WINDOW_WIDTH - 20, title_rect.bottom + 15), 
            2
        )
        
        # Create a section for game info
        section_y = title_rect.bottom + 30
        section_height = 120
        section_rect = pygame.Rect(BOARD_PX + 10, section_y, WINDOW_WIDTH - BOARD_PX - 20, section_height)
        pygame.draw.rect(screen, UI_SECTION_BG, section_rect, border_radius=5)
        
        # Draw the current turn with an indicator
        font = pygame.font.SysFont('Arial', 18)
        turn_label = font.render("Current Turn:", True, UI_TEXT)
        screen.blit(turn_label, (BOARD_PX + 20, section_y + 15))
        
        # Draw a colored circle to indicate the turn
        turn_color = WHITE_PIECE if self.turn == 'white' else BLACK_PIECE
        pygame.draw.circle(screen, turn_color, (BOARD_PX + 30, section_y + 50), 10)
        pygame.draw.circle(screen, UI_TEXT, (BOARD_PX + 30, section_y + 50), 10, 1)  # Border
        
        turn_text = f"{'White' if self.turn == 'white' else 'Black'}"
        turn_surface = font.render(turn_text, True, UI_TEXT)
        screen.blit(turn_surface, (BOARD_PX + 50, section_y + 42))
        
        # Draw the game mode
        mode_label = font.render("Game Mode:", True, UI_TEXT)
        screen.blit(mode_label, (BOARD_PX + 20, section_y + 70))
        
        mode_text = ""
        if self.game_mode == MODE_HUMAN_VS_HUMAN:
            mode_text = "Human vs Human"
        else:
            difficulty_text = "Easy" if self.ai_difficulty <= 5 else "Medium" if self.ai_difficulty <= 10 else "Hard"
            mode_text = f"Human vs AI ({difficulty_text})"
        
        mode_surface = font.render(mode_text, True, UI_TEXT)
        screen.blit(mode_surface, (BOARD_PX + 50, section_y + 95))
        
        # Draw AI thinking indicator
        if self.thinking:
            thinking_y = section_y + section_height + 20
            thinking_text = "AI is thinking..."
            thinking_surface = font.render(thinking_text, True, (255, 200, 0))
            
            # Create a pulsing effect
            alpha = int(128 + 127 * abs(math.sin(time.time() * 3)))
            thinking_surface.set_alpha(alpha)
            
            screen.blit(thinking_surface, (BOARD_PX + 20, thinking_y))
        
        # Draw game over message if applicable
        if self.game_over:
            game_over_y = section_y + section_height + 50
            game_over_section = pygame.Rect(
                BOARD_PX + 10, 
                game_over_y, 
                WINDOW_WIDTH - BOARD_PX - 20, 
                80
            )
            pygame.draw.rect(screen, (80, 0, 0), game_over_section, border_radius=5)
            
            game_over_font = pygame.font.SysFont('Arial', 22, bold=True)
            game_over_text = "Game Over"
            game_over_surface = game_over_font.render(game_over_text, True, (255, 100, 100))
            game_over_rect = game_over_surface.get_rect(
                midtop=(BOARD_PX + (WINDOW_WIDTH - BOARD_PX) // 2, game_over_y + 15)
            )
            screen.blit(game_over_surface, game_over_rect)
            
            result_surface = font.render(self.game_result, True, (255, 200, 200))
            result_rect = result_surface.get_rect(
                midtop=(BOARD_PX + (WINDOW_WIDTH - BOARD_PX) // 2, game_over_y + 45)
            )
            screen.blit(result_surface, result_rect)
    
    def get_square_at_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert screen coordinates to board coordinates."""
        x, y = pos
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        return row, col
    
    def select_piece(self, row: int, col: int) -> None:
        """Select a piece at the given position and calculate its legal moves."""
        if self.game_over or self.thinking or self.animating:
            return
            
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            piece = self.board[row][col]
            if piece and piece.color == self.turn:
                self.selected_piece = piece
                self.legal_moves = piece.get_legal_moves(self)
            else:
                self.selected_piece = None
                self.legal_moves = []
    
    def move_piece(self, row: int, col: int, piece_images: Optional[Dict[str, pygame.Surface]] = None) -> bool:
        """Move the selected piece to the given position if it's a legal move."""
        if self.game_over or self.thinking or self.animating:
            return False
            
        if self.selected_piece and (row, col) in self.legal_moves:
            old_row, old_col = self.selected_piece.position
            
            # Check for castling move
            is_castling = (self.selected_piece.piece_type == KING and abs(col - old_col) == 2)
            
            # Check for en passant capture
            is_en_passant = (self.selected_piece.piece_type == PAWN and 
                            old_col != col and 
                            self.board[row][col] is None)
            
            # Record the move
            self.move_history.append(((old_row, old_col), (row, col)))
            
            # Create animation if piece_images is provided
            if piece_images:
                self.animating = True
                
                # Create animation for the main piece
                piece_image = piece_images[self.selected_piece.get_image_key()]
                animated_piece = AnimatedPiece(
                    self.selected_piece.piece_type,
                    self.selected_piece.color,
                    (old_row, old_col),
                    (row, col),
                    piece_image
                )
                self.animated_pieces.append(animated_piece)
                
                # Create animation for the rook if castling
                if is_castling:
                    if col > old_col:  # Kingside castling
                        rook = self.board[row][7]
                        if rook:
                            rook_image = piece_images[rook.get_image_key()]
                            rook_animation = AnimatedPiece(
                                ROOK,
                                rook.color,
                                (row, 7),
                                (row, col - 1),
                                rook_image
                            )
                            self.animated_pieces.append(rook_animation)
                    else:  # Queenside castling
                        rook = self.board[row][0]
                        if rook:
                            rook_image = piece_images[rook.get_image_key()]
                            rook_animation = AnimatedPiece(
                                ROOK,
                                rook.color,
                                (row, 0),
                                (row, col + 1),
                                rook_image
                            )
                            self.animated_pieces.append(rook_animation)
            
            # Update the board
            self.board[row][col] = self.selected_piece
            self.board[old_row][old_col] = None
            
            # Update the piece's position
            self.selected_piece.position = (row, col)
            self.selected_piece.has_moved = True
            
            # Handle castling - move the rook as well
            if is_castling:
                if col > old_col:  # Kingside castling
                    # Move the rook from the right corner to the left of the king
                    rook = self.board[row][7]
                    if rook:
                        self.board[row][col - 1] = rook
                        self.board[row][7] = None
                        rook.position = (row, col - 1)
                        rook.has_moved = True
                else:  # Queenside castling
                    # Move the rook from the left corner to the right of the king
                    rook = self.board[row][0]
                    if rook:
                        self.board[row][col + 1] = rook
                        self.board[row][0] = None
                        rook.position = (row, col + 1)
                        rook.has_moved = True
            
            # Handle en passant capture
            if is_en_passant:
                # Remove the captured pawn
                self.board[old_row][col] = None
            
            # Track pawn double moves for en passant
            if self.selected_piece.piece_type == PAWN and abs(old_row - row) == 2:
                self.last_pawn_double_move = (row, col)
            else:
                self.last_pawn_double_move = None
            
            # Switch turns
            self.turn = 'black' if self.turn == 'white' else 'white'
            
            # Clear selection
            self.selected_piece = None
            self.legal_moves = []
            
            # Check if AI should make a move
            if self.game_mode == MODE_HUMAN_VS_AI and self.turn == 'black' and not self.game_over:
                if self.animating:
                    # If we're animating, set a flag to start AI thinking after animation completes
                    self.pending_ai_move = True
                else:
                    # Otherwise, start AI thinking immediately
                    self.thinking = True
                    self.ai_move_start_time = time.time()
                    # Set a random thinking time between MIN and MAX
                    self.ai_move_duration = MIN_AI_MOVE_TIME + (MAX_AI_MOVE_TIME - MIN_AI_MOVE_TIME) * np.random.random()
            
            return True
        
        return False
    
    def make_ai_move(self, piece_images: Optional[Dict[str, pygame.Surface]] = None) -> None:
        """Make a move with the AI."""
        if self.ai and self.turn == 'black' and not self.game_over:
            # Update the AI's internal board with the move history
            self.ai.update_board(self.move_history)
            
            # Get the best move from the AI
            ai_move = self.ai.get_best_move()
            
            if ai_move:
                from_pos, to_pos = ai_move
                from_row, from_col = from_pos
                to_row, to_col = to_pos
                
                # Make the move on our board
                piece = self.board[from_row][from_col]
                if piece:
                    # Record the move
                    self.move_history.append(((from_row, from_col), (to_row, to_col)))
                    
                    # Create animation if piece_images is provided
                    if piece_images:
                        self.animating = True
                        
                        # Create animation for the AI piece
                        piece_image = piece_images[piece.get_image_key()]
                        animated_piece = AnimatedPiece(
                            piece.piece_type,
                            piece.color,
                            (from_row, from_col),
                            (to_row, to_col),
                            piece_image
                        )
                        self.animated_pieces.append(animated_piece)
                    
                    # Update the board
                    self.board[to_row][to_col] = piece
                    self.board[from_row][from_col] = None
                    
                    # Update the piece's position
                    piece.position = (to_row, to_col)
                    piece.has_moved = True
                    
                    # Switch turns
                    self.turn = 'white'
            
            # Check for game over
            if self.ai.is_game_over():
                self.game_over = True
                self.game_result = self.ai.get_game_result()
        
        self.thinking = False
    
    def reset_game(self, game_mode: int = None, ai_difficulty: int = None) -> None:
        """Reset the game to the initial state."""
        if game_mode is not None:
            self.game_mode = game_mode
        
        if ai_difficulty is not None:
            self.ai_difficulty = ai_difficulty
            
        # Close the old AI if it exists
        if self.ai:
            self.ai.close()
            
        # Create a new AI if needed
        self.ai = ChessAI(difficulty=self.ai_difficulty) if self.game_mode == MODE_HUMAN_VS_AI else None
        
        # Reset the board
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected_piece = None
        self.legal_moves = []
        self.turn = 'white'
        self.move_history = []
        self.game_over = False
        self.game_result = ""
        self.thinking = False
        self.last_pawn_double_move = None
        
        # Set up the pieces
        self.setup_pieces()

def main() -> None:
    """Main game loop."""
    clock = pygame.time.Clock()
    board = ChessBoard(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=10)
    piece_images = create_piece_images()
    dragging = False
    drag_piece = None
    drag_start_pos = None
    
    # Create UI buttons with a better layout
    button_width = 180
    button_height = 40
    button_x = BOARD_PX + (WINDOW_WIDTH - BOARD_PX - button_width) // 2
    button_spacing = 15
    
    # Calculate starting Y position for buttons (positioned at the bottom of the UI panel)
    button_start_y = WINDOW_HEIGHT - (button_height + button_spacing) * 5 - button_spacing
    
    # Create mode buttons
    buttons = [
        Button(button_x, button_start_y, button_width, button_height, "Human vs Human"),
        Button(button_x, button_start_y + (button_height + button_spacing), button_width, button_height, "Human vs AI (Easy)"),
        Button(button_x, button_start_y + (button_height + button_spacing) * 2, button_width, button_height, "Human vs AI (Medium)"),
        Button(button_x, button_start_y + (button_height + button_spacing) * 3, button_width, button_height, "Human vs AI (Hard)")
    ]
    
    # Add a reset button
    reset_button = Button(
        button_x, 
        button_start_y + (button_height + button_spacing) * 4, 
        button_width, 
        button_height, 
        "Reset Game", 
        color=(150, 50, 50),
        hover_color=(180, 70, 70),
        active_color=(200, 90, 90)
    )
    buttons.append(reset_button)
    
    # Set the active button based on current game mode
    if board.game_mode == MODE_HUMAN_VS_HUMAN:
        buttons[0].set_active(True)
    else:
        if board.ai_difficulty <= 5:
            buttons[1].set_active(True)
        elif board.ai_difficulty <= 10:
            buttons[2].set_active(True)
        else:
            buttons[3].set_active(True)
    
    running = True
    
    while running:
        current_time = time.time()
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_clicked = True
                    if mouse_pos[0] < BOARD_PX and not board.animating:  # Click on the board
                        row, col = board.get_square_at_pos(event.pos)
                        # Store the starting position for drag and drop
                        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                            piece = board.board[row][col]
                            if piece and piece.color == board.turn:
                                drag_piece = piece
                                drag_start_pos = (row, col)
                                board.select_piece(row, col)
                                dragging = True
                            else:
                                # Clicking on an empty square or opponent's piece
                                # Try to move the selected piece if one is selected
                                if board.selected_piece:
                                    board.move_piece(row, col, piece_images)
                                    board.selected_piece = None
                                    board.legal_moves = []
                                else:
                                    # Just select the square (might be opponent's piece)
                                    board.select_piece(row, col)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:  # Left mouse button
                    if mouse_pos[0] < BOARD_PX and not board.animating:  # Release on the board
                        row, col = board.get_square_at_pos(event.pos)
                        # Only try to move if we're releasing on a different square
                        if drag_start_pos != (row, col):
                            moved = board.move_piece(row, col, piece_images)
                            if not moved:
                                # If the move was invalid, clear selection
                                board.selected_piece = None
                                board.legal_moves = []
                    dragging = False
                    drag_piece = None
                    drag_start_pos = None
        
        # Update animations
        board.update_animations()
        
        # Check if AI should make a move after thinking time has elapsed
        if board.thinking and current_time - board.ai_move_start_time >= board.ai_move_duration:
            board.make_ai_move(piece_images)
        
        # Update buttons
        for button in buttons:
            button.update(mouse_pos)
        
        # Handle button clicks
        for i, button in enumerate(buttons):
            if button.is_clicked(mouse_pos, mouse_clicked) and not board.animating:
                # Reset active state for all buttons
                for b in buttons:
                    b.set_active(False)
                
                # Set this button as active
                button.set_active(True)
                
                # Handle button actions
                if i == 0:  # Human vs Human
                    board.reset_game(game_mode=MODE_HUMAN_VS_HUMAN)
                elif i == 1:  # Human vs AI (Easy)
                    board.reset_game(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=5)
                elif i == 2:  # Human vs AI (Medium)
                    board.reset_game(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=10)
                elif i == 3:  # Human vs AI (Hard)
                    board.reset_game(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=15)
                elif i == 4:  # Reset Game
                    # Keep the same mode but reset the game
                    board.reset_game()
                    # Reset the active state for the reset button
                    button.set_active(False)
                    # Set the appropriate mode button as active
                    if board.game_mode == MODE_HUMAN_VS_HUMAN:
                        buttons[0].set_active(True)
                    else:
                        if board.ai_difficulty <= 5:
                            buttons[1].set_active(True)
                        elif board.ai_difficulty <= 10:
                            buttons[2].set_active(True)
                        else:
                            buttons[3].set_active(True)
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Draw the board and pieces
        board.draw(screen, piece_images)
        
        # Draw the dragged piece at the mouse position if dragging
        if dragging and drag_piece and not board.animating:
            image = piece_images[drag_piece.get_image_key()]
            # Center the piece on the mouse
            screen.blit(image, (mouse_pos[0] - SQUARE_SIZE // 2, mouse_pos[1] - SQUARE_SIZE // 2))
        
        # Draw buttons
        for button in buttons:
            button.draw(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Clean up
    if board.ai:
        board.ai.close()
    
    pygame.quit()

if __name__ == "__main__":
    main() 