import pygame
from typing import Tuple, Dict, Optional, List, Any

from constants import (
    TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, UI_BG, UI_PANEL_BORDER, UI_TEXT,
    UI_HEADING, UI_SECTION_BG, UI_BUTTON, UI_BUTTON_HOVER, UI_BUTTON_ACTIVE,
    FLOOR_TILE, WALL_TILE, DOOR_TILE, ENEMY_TILE, CHEST_TILE, PLAYER_TILE
)
from models.dungeon import Dungeon, Enemy, Chest
from models.player import Player
from ui.button import Button


class DungeonUI:
    """UI for displaying and interacting with the dungeon."""
    
    def __init__(self, dungeon: Dungeon, player: Player, tile_images: Dict[str, pygame.Surface]):
        """
        Initialize the dungeon UI.
        
        Args:
            dungeon: The dungeon to display
            player: The player character
            tile_images: Dictionary of tile images
        """
        self.dungeon = dungeon
        self.player = player
        self.tile_images = tile_images
        
        # Camera position (centered on player)
        self.camera_x = 0
        self.camera_y = 0
        
        # Visible area in tiles
        self.visible_width = WINDOW_WIDTH // TILE_SIZE
        self.visible_height = WINDOW_HEIGHT // TILE_SIZE
        
        # UI elements
        self.buttons = []
        self._create_buttons()
        
        # Interaction panel
        self.show_interaction_panel = False
        self.interaction_target = None
        self.interaction_buttons = []
        
        # Message log
        self.messages: List[Tuple[str, int]] = []  # (message, time_remaining)
        self.max_messages = 5
        self.message_duration = 180  # frames
    
    def _create_buttons(self) -> None:
        """Create UI buttons."""
        button_width = 120
        button_height = 40
        button_spacing = 10
        
        # End turn button
        self.end_turn_button = Button(
            WINDOW_WIDTH - button_width - button_spacing,
            WINDOW_HEIGHT - button_height - button_spacing,
            button_width,
            button_height,
            "End Turn"
        )
        self.buttons.append(self.end_turn_button)
        
        # Inventory button
        self.inventory_button = Button(
            WINDOW_WIDTH - button_width - button_spacing,
            WINDOW_HEIGHT - 2 * (button_height + button_spacing),
            button_width,
            button_height,
            "Inventory"
        )
        self.buttons.append(self.inventory_button)
        
        # Interact button
        self.interact_button = Button(
            WINDOW_WIDTH - button_width - button_spacing,
            WINDOW_HEIGHT - 3 * (button_height + button_spacing),
            button_width,
            button_height,
            "Interact"
        )
        self.buttons.append(self.interact_button)
    
    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> str:
        """
        Update the dungeon UI based on mouse input.
        
        Args:
            mouse_pos: Current mouse position
            mouse_clicked: Whether the mouse was clicked
            
        Returns:
            Action to take: "end_turn", "inventory", "interact", or empty string for no action
        """
        # Update camera position to center on player
        player_x, player_y = self.player.get_current_position()
        self.camera_x = player_x - self.visible_width // 2
        self.camera_y = player_y - self.visible_height // 2
        
        # Update buttons
        for button in self.buttons:
            button.update(mouse_pos)
        
        # Update interaction buttons if panel is shown
        if self.show_interaction_panel:
            for button in self.interaction_buttons:
                button.update(mouse_pos)
        
        # Handle button clicks
        if mouse_clicked:
            if self.end_turn_button.is_clicked(mouse_pos, mouse_clicked):
                return "end_turn"
            
            elif self.inventory_button.is_clicked(mouse_pos, mouse_clicked):
                return "inventory"
            
            elif self.interact_button.is_clicked(mouse_pos, mouse_clicked):
                return "interact"
            
            # Handle interaction panel buttons
            if self.show_interaction_panel:
                for i, button in enumerate(self.interaction_buttons):
                    if button.is_clicked(mouse_pos, mouse_clicked):
                        return f"interaction_{i}"
            
            # Check if a tile was clicked for movement
            tile_x, tile_y = self._screen_to_tile(mouse_pos)
            if self._is_valid_movement_target(tile_x, tile_y):
                return f"move_{tile_x}_{tile_y}"
        
        # Update message timers
        self._update_messages()
        
        return ""
    
    def _screen_to_tile(self, screen_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert screen coordinates to tile coordinates."""
        screen_x, screen_y = screen_pos
        tile_x = int(self.camera_x + screen_x // TILE_SIZE)
        tile_y = int(self.camera_y + screen_y // TILE_SIZE)
        return tile_x, tile_y
    
    def _tile_to_screen(self, tile_pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert tile coordinates to screen coordinates."""
        tile_x, tile_y = tile_pos
        screen_x = int((tile_x - self.camera_x) * TILE_SIZE)
        screen_y = int((tile_y - self.camera_y) * TILE_SIZE)
        return screen_x, screen_y
    
    def _is_valid_movement_target(self, tile_x: int, tile_y: int) -> bool:
        """Check if a tile is a valid movement target."""
        # Check if the tile is within the player's movement range
        player_x, player_y = self.player.position
        distance = abs(tile_x - player_x) + abs(tile_y - player_y)
        
        if distance > self.player.movement_range:
            return False
        
        # Check if the tile is walkable
        return self.dungeon.is_walkable(tile_x, tile_y)
    
    def show_interaction(self, target: Any) -> None:
        """
        Show the interaction panel for a target.
        
        Args:
            target: The entity to interact with
        """
        self.show_interaction_panel = True
        self.interaction_target = target
        self.interaction_buttons = []
        
        # Create buttons based on the target type
        button_width = 150
        button_height = 40
        button_spacing = 10
        panel_x = WINDOW_WIDTH // 2 - 100
        panel_y = WINDOW_HEIGHT // 2 - 100
        
        if isinstance(target, Enemy):
            # Enemy interaction
            combat_button = Button(
                panel_x,
                panel_y + button_spacing,
                button_width,
                button_height,
                "Start Combat"
            )
            self.interaction_buttons.append(combat_button)
            
            examine_button = Button(
                panel_x,
                panel_y + button_height + 2 * button_spacing,
                button_width,
                button_height,
                "Examine"
            )
            self.interaction_buttons.append(examine_button)
        
        elif isinstance(target, Chest):
            # Chest interaction
            open_button = Button(
                panel_x,
                panel_y + button_spacing,
                button_width,
                button_height,
                "Open Chest"
            )
            self.interaction_buttons.append(open_button)
            
            examine_button = Button(
                panel_x,
                panel_y + button_height + 2 * button_spacing,
                button_width,
                button_height,
                "Examine"
            )
            self.interaction_buttons.append(examine_button)
        
        # Add a cancel button
        cancel_button = Button(
            panel_x,
            panel_y + 2 * button_height + 3 * button_spacing,
            button_width,
            button_height,
            "Cancel"
        )
        self.interaction_buttons.append(cancel_button)
    
    def hide_interaction(self) -> None:
        """Hide the interaction panel."""
        self.show_interaction_panel = False
        self.interaction_target = None
        self.interaction_buttons = []
    
    def add_message(self, message: str) -> None:
        """Add a message to the message log."""
        self.messages.append((message, self.message_duration))
        
        # Trim messages if we have too many
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def _update_messages(self) -> None:
        """Update message timers and remove expired messages."""
        for i in range(len(self.messages) - 1, -1, -1):
            message, time_remaining = self.messages[i]
            time_remaining -= 1
            
            if time_remaining <= 0:
                self.messages.pop(i)
            else:
                self.messages[i] = (message, time_remaining)
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the dungeon UI.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Clear the screen
        screen.fill(UI_BG)
        
        # Draw the visible portion of the dungeon
        self._draw_dungeon(screen)
        
        # Draw the player
        self._draw_player(screen)
        
        # Draw UI elements
        self._draw_ui(screen)
        
        # Draw interaction panel if shown
        if self.show_interaction_panel:
            self._draw_interaction_panel(screen)
        
        # Draw message log
        self._draw_messages(screen)
    
    def _draw_dungeon(self, screen: pygame.Surface) -> None:
        """Draw the visible portion of the dungeon."""
        start_x = max(0, int(self.camera_x))
        start_y = max(0, int(self.camera_y))
        end_x = min(self.dungeon.width, int(self.camera_x + self.visible_width + 1))
        end_y = min(self.dungeon.height, int(self.camera_y + self.visible_height + 1))
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.dungeon.grid[y][x]
                
                # Only draw tiles that are visible or have been discovered
                if tile.visible or tile.discovered:
                    screen_x, screen_y = self._tile_to_screen((x, y))
                    
                    # Draw the tile
                    tile_image = self.tile_images[tile.tile_type]
                    
                    # Darken tiles that are discovered but not currently visible
                    if tile.discovered and not tile.visible:
                        # Create a darkened copy of the tile image
                        darkened = tile_image.copy()
                        dark_overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        dark_overlay.fill((0, 0, 0, 128))  # Semi-transparent black
                        darkened.blit(dark_overlay, (0, 0))
                        screen.blit(darkened, (screen_x, screen_y))
                    else:
                        screen.blit(tile_image, (screen_x, screen_y))
                    
                    # Draw entity on the tile if visible
                    if tile.visible and tile.entity:
                        if isinstance(tile.entity, Enemy):
                            enemy_image = self.tile_images[ENEMY_TILE]
                            screen.blit(enemy_image, (screen_x, screen_y))
                        elif isinstance(tile.entity, Chest):
                            chest_image = self.tile_images[CHEST_TILE]
                            screen.blit(chest_image, (screen_x, screen_y))
    
    def _draw_player(self, screen: pygame.Surface) -> None:
        """Draw the player character."""
        player_x, player_y = self.player.get_current_position()
        screen_x, screen_y = self._tile_to_screen((player_x, player_y))
        
        player_image = self.tile_images[PLAYER_TILE]
        screen.blit(player_image, (screen_x, screen_y))
    
    def _draw_ui(self, screen: pygame.Surface) -> None:
        """Draw UI elements."""
        # Draw player stats
        font = pygame.font.SysFont('Arial', 18)
        
        # Draw health
        health_text = font.render(f"Health: {self.player.health}/{self.player.max_health}", True, UI_TEXT)
        screen.blit(health_text, (10, 10))
        
        # Draw movement range (for combat)
        moves_text = font.render(f"Movement Range: {self.player.movement_range}", True, UI_TEXT)
        screen.blit(moves_text, (10, 35))
        
        # Draw player stats
        command_text = font.render(f"Command: {self.player.command}", True, UI_TEXT)
        screen.blit(command_text, (10, 60))
        
        tactics_text = font.render(f"Tactics: {self.player.tactics}", True, UI_TEXT)
        screen.blit(tactics_text, (10, 85))
        
        perception_text = font.render(f"Perception: {self.player.perception}", True, UI_TEXT)
        screen.blit(perception_text, (10, 110))
        
        arcana_text = font.render(f"Arcana: {self.player.arcana}", True, UI_TEXT)
        screen.blit(arcana_text, (10, 135))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
    
    def _draw_interaction_panel(self, screen: pygame.Surface) -> None:
        """Draw the interaction panel."""
        # Draw panel background
        panel_width = 300
        panel_height = 250
        panel_x = WINDOW_WIDTH // 2 - panel_width // 2
        panel_y = WINDOW_HEIGHT // 2 - panel_height // 2
        
        pygame.draw.rect(screen, UI_SECTION_BG, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, UI_PANEL_BORDER, (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw panel title
        font = pygame.font.SysFont('Arial', 24, bold=True)
        title_text = "Interaction"
        
        if isinstance(self.interaction_target, Enemy):
            title_text = f"Enemy: {self.interaction_target.enemy_type.capitalize()}"
        elif isinstance(self.interaction_target, Chest):
            title_text = f"Chest: {self.interaction_target.chest_type.capitalize()}"
        
        title = font.render(title_text, True, UI_HEADING)
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 10))
        
        # Draw interaction buttons
        for button in self.interaction_buttons:
            button.draw(screen)
    
    def _draw_messages(self, screen: pygame.Surface) -> None:
        """Draw the message log."""
        if not self.messages:
            return
        
        font = pygame.font.SysFont('Arial', 16)
        message_height = 25
        message_padding = 5
        
        # Draw message background
        total_height = len(self.messages) * message_height + 2 * message_padding
        pygame.draw.rect(screen, UI_SECTION_BG, (10, WINDOW_HEIGHT - total_height - 10, WINDOW_WIDTH - 20, total_height))
        pygame.draw.rect(screen, UI_PANEL_BORDER, (10, WINDOW_HEIGHT - total_height - 10, WINDOW_WIDTH - 20, total_height), 2)
        
        # Draw messages
        for i, (message, _) in enumerate(self.messages):
            y_pos = WINDOW_HEIGHT - total_height - 10 + message_padding + i * message_height
            message_text = font.render(message, True, UI_TEXT)
            screen.blit(message_text, (20, y_pos)) 