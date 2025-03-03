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

"""
This file is kept for backward compatibility.
It imports all the necessary components from the refactored modules.
"""

from constants import *
from models.chess_board import ChessBoard
from models.chess_piece import ChessPiece
from ui.button import Button
from ui.animations import AnimatedPiece
from main import main

if __name__ == "__main__":
    main()