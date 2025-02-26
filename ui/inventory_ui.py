import pygame
from typing import List, Tuple, Dict, Optional, Any

from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, SQUARE_SIZE, UI_BG, UI_PANEL_BORDER, UI_TEXT,
    UI_HEADING, UI_SECTION_BG, UI_BUTTON, UI_BUTTON_HOVER, UI_BUTTON_ACTIVE
)
from models.chess_piece import RPGChessPiece
from models.player_inventory import PlayerInventory
from ui.button import Button


class InventoryUI:
    """UI for displaying and managing the player's inventory of chess pieces."""
    
    def __init__(self, inventory: PlayerInventory):
        """
        Initialize the inventory UI.
        
        Args:
            inventory: The player's inventory
        """
        self.inventory = inventory
        self.active_tab = "active"  # "active" or "reserve"
        self.selected_piece_index = -1
        self.selected_piece = None
        self.scroll_offset = 0
        self.max_pieces_per_page = 8
        
        # Create UI buttons
        button_width = 180
        button_height = 40
        button_spacing = 15
        
        # Tab buttons
        self.active_tab_button = Button(
            WINDOW_WIDTH // 4 - button_width // 2,
            50,
            button_width,
            button_height,
            "Active Pieces",
            color=UI_BUTTON_ACTIVE if self.active_tab == "active" else UI_BUTTON
        )
        
        self.reserve_tab_button = Button(
            WINDOW_WIDTH * 3 // 4 - button_width // 2,
            50,
            button_width,
            button_height,
            "Reserve Pieces",
            color=UI_BUTTON if self.active_tab == "active" else UI_BUTTON_ACTIVE
        )
        
        # Action buttons
        button_y = WINDOW_HEIGHT - button_height - button_spacing
        
        self.move_button = Button(
            WINDOW_WIDTH // 2 - button_width - button_spacing,
            button_y,
            button_width,
            button_height,
            "Move to Reserve" if self.active_tab == "active" else "Move to Active"
        )
        
        self.back_button = Button(
            WINDOW_WIDTH // 2 + button_spacing,
            button_y,
            button_width,
            button_height,
            "Back to Game"
        )
        
        # Scroll buttons
        self.scroll_up_button = Button(
            WINDOW_WIDTH - 50,
            150,
            40,
            40,
            "↑"
        )
        
        self.scroll_down_button = Button(
            WINDOW_WIDTH - 50,
            200,
            40,
            40,
            "↓"
        )
    
    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> str:
        """
        Update the inventory UI based on mouse input.
        
        Args:
            mouse_pos: Current mouse position
            mouse_clicked: Whether the mouse was clicked
            
        Returns:
            Action to take: "back" to return to game, empty string for no action
        """
        # Update buttons
        self.active_tab_button.update(mouse_pos)
        self.reserve_tab_button.update(mouse_pos)
        self.move_button.update(mouse_pos)
        self.back_button.update(mouse_pos)
        self.scroll_up_button.update(mouse_pos)
        self.scroll_down_button.update(mouse_pos)
        
        # Handle button clicks
        if mouse_clicked:
            # Tab buttons
            if self.active_tab_button.is_clicked(mouse_pos, mouse_clicked):
                self.active_tab = "active"
                self.active_tab_button.set_active(True)
                self.reserve_tab_button.set_active(False)
                self.selected_piece_index = -1
                self.selected_piece = None
                self.scroll_offset = 0
                self.move_button.text = "Move to Reserve"
            
            elif self.reserve_tab_button.is_clicked(mouse_pos, mouse_clicked):
                self.active_tab = "reserve"
                self.active_tab_button.set_active(False)
                self.reserve_tab_button.set_active(True)
                self.selected_piece_index = -1
                self.selected_piece = None
                self.scroll_offset = 0
                self.move_button.text = "Move to Active"
            
            # Action buttons
            elif self.move_button.is_clicked(mouse_pos, mouse_clicked):
                if self.selected_piece_index >= 0:
                    if self.active_tab == "active":
                        # Don't allow moving the last piece from active
                        if len(self.inventory.active_pieces) > 1:
                            self.inventory.move_to_reserve(self.selected_piece_index)
                            self.selected_piece_index = -1
                            self.selected_piece = None
                    else:  # reserve tab
                        if len(self.inventory.active_pieces) < self.inventory.command_stat:
                            self.inventory.move_to_active(self.selected_piece_index)
                            self.selected_piece_index = -1
                            self.selected_piece = None
            
            elif self.back_button.is_clicked(mouse_pos, mouse_clicked):
                # Save inventory before returning
                self.inventory.save_inventory()
                return "back"
            
            # Scroll buttons
            elif self.scroll_up_button.is_clicked(mouse_pos, mouse_clicked):
                self.scroll_offset = max(0, self.scroll_offset - 1)
            
            elif self.scroll_down_button.is_clicked(mouse_pos, mouse_clicked):
                pieces = self.inventory.active_pieces if self.active_tab == "active" else self.inventory.reserve_pieces
                max_offset = max(0, len(pieces) - self.max_pieces_per_page)
                self.scroll_offset = min(max_offset, self.scroll_offset + 1)
            
            # Check if a piece was clicked
            else:
                self._handle_piece_click(mouse_pos)
        
        return ""
    
    def _handle_piece_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle clicks on pieces in the inventory."""
        pieces = self.inventory.active_pieces if self.active_tab == "active" else self.inventory.reserve_pieces
        
        # Calculate the area where pieces are displayed
        piece_area_x = 50
        piece_area_y = 120
        piece_area_width = WINDOW_WIDTH - 100
        piece_area_height = WINDOW_HEIGHT - 200
        
        # Check if click is within the piece display area
        if (piece_area_x <= mouse_pos[0] <= piece_area_x + piece_area_width and
            piece_area_y <= mouse_pos[1] <= piece_area_y + piece_area_height):
            
            # Calculate which piece was clicked
            piece_height = 70
            piece_spacing = 10
            
            for i in range(min(self.max_pieces_per_page, len(pieces) - self.scroll_offset)):
                piece_index = i + self.scroll_offset
                piece_y = piece_area_y + i * (piece_height + piece_spacing)
                
                if piece_y <= mouse_pos[1] <= piece_y + piece_height:
                    self.selected_piece_index = piece_index
                    self.selected_piece = pieces[piece_index]
                    break
    
    def draw(self, screen: pygame.Surface, piece_images: Dict[str, pygame.Surface]) -> None:
        """
        Draw the inventory UI.
        
        Args:
            screen: Pygame surface to draw on
            piece_images: Dictionary of piece images
        """
        # Draw background
        screen.fill(UI_BG)
        
        # Draw title
        font = pygame.font.SysFont('Arial', 32, bold=True)
        title = font.render("Chess Piece Inventory", True, UI_HEADING)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 10))
        
        # Draw player stats
        self._draw_player_stats(screen)
        
        # Draw tab buttons
        self.active_tab_button.draw(screen)
        self.reserve_tab_button.draw(screen)
        
        # Draw piece list
        self._draw_piece_list(screen, piece_images)
        
        # Draw selected piece details
        if self.selected_piece:
            self._draw_piece_details(screen, self.selected_piece, piece_images)
        
        # Draw action buttons
        self.move_button.draw(screen)
        self.back_button.draw(screen)
        
        # Draw scroll buttons if needed
        pieces = self.inventory.active_pieces if self.active_tab == "active" else self.inventory.reserve_pieces
        if len(pieces) > self.max_pieces_per_page:
            self.scroll_up_button.draw(screen)
            self.scroll_down_button.draw(screen)
    
    def _draw_player_stats(self, screen: pygame.Surface) -> None:
        """Draw the player's stats."""
        font = pygame.font.SysFont('Arial', 18)
        
        # Draw gold
        gold_text = font.render(f"Gold: {self.inventory.gold}", True, UI_TEXT)
        screen.blit(gold_text, (20, 20))
        
        # Draw command stat
        command_text = font.render(f"Command: {self.inventory.command_stat}", True, UI_TEXT)
        screen.blit(command_text, (20, 45))
        
        # Draw other stats
        tactics_text = font.render(f"Tactics: {self.inventory.tactics_stat}", True, UI_TEXT)
        screen.blit(tactics_text, (150, 20))
        
        perception_text = font.render(f"Perception: {self.inventory.perception_stat}", True, UI_TEXT)
        screen.blit(perception_text, (150, 45))
        
        arcana_text = font.render(f"Arcana: {self.inventory.arcana_stat}", True, UI_TEXT)
        screen.blit(arcana_text, (300, 20))
    
    def _draw_piece_list(self, screen: pygame.Surface, piece_images: Dict[str, pygame.Surface]) -> None:
        """Draw the list of pieces in the current tab."""
        pieces = self.inventory.active_pieces if self.active_tab == "active" else self.inventory.reserve_pieces
        
        # Draw section background
        pygame.draw.rect(screen, UI_SECTION_BG, (50, 120, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 200))
        pygame.draw.rect(screen, UI_PANEL_BORDER, (50, 120, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 200), 2)
        
        # Draw pieces
        font = pygame.font.SysFont('Arial', 16)
        small_font = pygame.font.SysFont('Arial', 14)
        
        piece_height = 70
        piece_spacing = 10
        
        # Display message if no pieces
        if not pieces:
            no_pieces_text = font.render("No pieces in this collection.", True, UI_TEXT)
            screen.blit(no_pieces_text, (WINDOW_WIDTH // 2 - no_pieces_text.get_width() // 2, 200))
            return
        
        # Draw visible pieces
        for i in range(min(self.max_pieces_per_page, len(pieces) - self.scroll_offset)):
            piece_index = i + self.scroll_offset
            piece = pieces[piece_index]
            
            y_pos = 120 + i * (piece_height + piece_spacing)
            
            # Highlight selected piece
            if piece_index == self.selected_piece_index:
                pygame.draw.rect(screen, UI_BUTTON_ACTIVE, (50, y_pos, WINDOW_WIDTH - 100, piece_height))
            
            # Draw piece image
            image = piece_images[piece.get_image_key()]
            small_image = pygame.transform.scale(image, (50, 50))
            screen.blit(small_image, (60, y_pos + 10))
            
            # Draw piece info
            name_text = font.render(f"{piece.color.capitalize()} {piece.piece_type.capitalize()}", True, UI_TEXT)
            screen.blit(name_text, (120, y_pos + 10))
            
            rarity_text = small_font.render(f"Rarity: {piece.rarity}", True, UI_TEXT)
            screen.blit(rarity_text, (120, y_pos + 30))
            
            level_text = small_font.render(f"Level: {piece.level}", True, UI_TEXT)
            screen.blit(level_text, (250, y_pos + 10))
            
            durability_text = small_font.render(
                f"Durability: {piece.current_durability}/{piece.max_durability}", 
                True, 
                UI_TEXT
            )
            screen.blit(durability_text, (250, y_pos + 30))
            
            # Draw effectiveness
            effectiveness = piece.get_effectiveness()
            effectiveness_text = small_font.render(
                f"Effectiveness: {effectiveness:.2f}x", 
                True, 
                UI_TEXT
            )
            screen.blit(effectiveness_text, (400, y_pos + 10))
    
    def _draw_piece_details(self, screen: pygame.Surface, piece: RPGChessPiece, 
                           piece_images: Dict[str, pygame.Surface]) -> None:
        """Draw detailed information about the selected piece."""
        # Draw section background
        detail_x = WINDOW_WIDTH - 300
        detail_y = 120
        detail_width = 250
        detail_height = 300
        
        pygame.draw.rect(screen, UI_SECTION_BG, (detail_x, detail_y, detail_width, detail_height))
        pygame.draw.rect(screen, UI_PANEL_BORDER, (detail_x, detail_y, detail_width, detail_height), 2)
        
        # Draw section title
        font = pygame.font.SysFont('Arial', 20, bold=True)
        title = font.render("Piece Details", True, UI_HEADING)
        screen.blit(title, (detail_x + detail_width // 2 - title.get_width() // 2, detail_y + 10))
        
        # Draw piece image
        image = piece_images[piece.get_image_key()]
        screen.blit(image, (detail_x + detail_width // 2 - SQUARE_SIZE // 2, detail_y + 40))
        
        # Draw piece info
        info_font = pygame.font.SysFont('Arial', 16)
        y_offset = detail_y + 40 + SQUARE_SIZE + 10
        
        # Basic info
        name_text = info_font.render(f"{piece.color.capitalize()} {piece.piece_type.capitalize()}", True, UI_TEXT)
        screen.blit(name_text, (detail_x + 10, y_offset))
        y_offset += 25
        
        rarity_text = info_font.render(f"Rarity: {piece.rarity}", True, UI_TEXT)
        screen.blit(rarity_text, (detail_x + 10, y_offset))
        y_offset += 25
        
        level_text = info_font.render(f"Level: {piece.level}", True, UI_TEXT)
        screen.blit(level_text, (detail_x + 10, y_offset))
        y_offset += 25
        
        # XP info
        if piece.level < 10:
            xp_text = info_font.render(f"XP: {piece.xp}/{piece.xp_to_next_level}", True, UI_TEXT)
        else:
            xp_text = info_font.render(f"XP: MAX LEVEL", True, UI_TEXT)
        screen.blit(xp_text, (detail_x + 10, y_offset))
        y_offset += 25
        
        # Durability
        durability_text = info_font.render(
            f"Durability: {piece.current_durability}/{piece.max_durability}", 
            True, 
            UI_TEXT
        )
        screen.blit(durability_text, (detail_x + 10, y_offset))
        y_offset += 25
        
        # Effectiveness
        effectiveness = piece.get_effectiveness()
        effectiveness_text = info_font.render(
            f"Effectiveness: {effectiveness:.2f}x", 
            True, 
            UI_TEXT
        )
        screen.blit(effectiveness_text, (detail_x + 10, y_offset))
        y_offset += 25
        
        # Ability slots
        ability_text = info_font.render(
            f"Ability Slots: {len(piece.special_abilities)}/{piece.ability_slots}", 
            True, 
            UI_TEXT
        )
        screen.blit(ability_text, (detail_x + 10, y_offset))
        y_offset += 25
        
        # Equipment slots
        equipment_text = info_font.render(
            f"Equipment Slots: {len(piece.equipment)}/{piece.equipment_slots}", 
            True, 
            UI_TEXT
        )
        screen.blit(equipment_text, (detail_x + 10, y_offset))
        y_offset += 25
        
        # Special abilities
        if piece.special_abilities:
            abilities_title = info_font.render("Special Abilities:", True, UI_TEXT)
            screen.blit(abilities_title, (detail_x + 10, y_offset))
            y_offset += 25
            
            for ability in piece.special_abilities:
                ability_text = info_font.render(f"- {ability}", True, UI_TEXT)
                screen.blit(ability_text, (detail_x + 20, y_offset))
                y_offset += 20
        else:
            no_abilities_text = info_font.render("No special abilities", True, UI_TEXT)
            screen.blit(no_abilities_text, (detail_x + 10, y_offset)) 