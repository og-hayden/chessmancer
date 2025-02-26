import pygame
import math
from typing import Tuple

from constants import SQUARE_SIZE, ANIMATION_SPEED

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