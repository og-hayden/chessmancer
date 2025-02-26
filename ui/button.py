import pygame
from typing import Tuple, Optional

from constants import UI_BUTTON, UI_BUTTON_HOVER, UI_BUTTON_ACTIVE, UI_BUTTON_TEXT

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