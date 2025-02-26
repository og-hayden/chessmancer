import pygame
import time
from typing import List

from constants import (
    FPS, BOARD_PX, WINDOW_WIDTH, WINDOW_HEIGHT, SQUARE_SIZE, BLACK,
    MODE_HUMAN_VS_HUMAN, MODE_HUMAN_VS_AI, screen, create_piece_images
)
from models.chess_board import ChessBoard
from models.player_inventory import PlayerInventory
from models.chess_piece import RPGChessPiece
from ui.button import Button
from ui.inventory_ui import InventoryUI

def main() -> None:
    """Main game loop."""
    clock = pygame.time.Clock()
    board = ChessBoard(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=10)
    piece_images = create_piece_images()
    dragging = False
    drag_piece = None
    drag_start_pos = None
    
    # Initialize player inventory
    player_inventory = PlayerInventory()
    inventory_ui = InventoryUI(player_inventory)
    show_inventory = False
    
    # Create UI buttons with a better layout
    button_width = 180
    button_height = 40
    button_x = BOARD_PX + (WINDOW_WIDTH - BOARD_PX - button_width) // 2
    button_spacing = 15
    
    # Calculate starting Y position for buttons (positioned at the bottom of the UI panel)
    button_start_y = WINDOW_HEIGHT - (button_height + button_spacing) * 6 - button_spacing
    
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
    
    # Add an inventory button
    inventory_button = Button(
        button_x, 
        button_start_y + (button_height + button_spacing) * 5, 
        button_width, 
        button_height, 
        "Inventory", 
        color=(50, 100, 150),
        hover_color=(70, 120, 180),
        active_color=(90, 140, 200)
    )
    buttons.append(inventory_button)
    
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
                    if show_inventory:
                        show_inventory = False
                    else:
                        running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_clicked = True
                    if not show_inventory and mouse_pos[0] < BOARD_PX and not board.animating:  # Click on the board
                        row, col = board.get_square_at_pos(event.pos)
                        # Store the starting position for drag and drop
                        if 0 <= row < 8 and 0 <= col < 8:
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
                    if not show_inventory and mouse_pos[0] < BOARD_PX and not board.animating:  # Release on the board
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
        
        # Handle inventory UI if it's shown
        if show_inventory:
            inventory_action = inventory_ui.update(mouse_pos, mouse_clicked)
            if inventory_action == "back":
                show_inventory = False
        else:
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
                    for b in buttons[:5]:  # Only reset game mode buttons, not inventory
                        b.set_active(False)
                    
                    # Handle button actions
                    if i == 0:  # Human vs Human
                        button.set_active(True)
                        board.reset_game(game_mode=MODE_HUMAN_VS_HUMAN)
                    elif i == 1:  # Human vs AI (Easy)
                        button.set_active(True)
                        board.reset_game(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=5)
                    elif i == 2:  # Human vs AI (Medium)
                        button.set_active(True)
                        board.reset_game(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=10)
                    elif i == 3:  # Human vs AI (Hard)
                        button.set_active(True)
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
                    elif i == 5:  # Inventory
                        show_inventory = True
        
        # Clear the screen
        screen.fill(BLACK)
        
        if show_inventory:
            # Draw inventory UI
            inventory_ui.draw(screen, piece_images)
        else:
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
            
            # Check for game over and handle rewards
            if board.game_over and not board.rewards_given:
                _handle_game_rewards(board, player_inventory)
                board.rewards_given = True
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Save inventory before quitting
    player_inventory.save_inventory()
    
    # Clean up
    if board.ai:
        board.ai.close()
    
    pygame.quit()

def _handle_game_rewards(board: ChessBoard, inventory: PlayerInventory) -> None:
    """
    Handle rewards after a game is completed.
    
    Args:
        board: The chess board with game result
        inventory: The player's inventory
    """
    # Only give rewards if player won
    if "White wins" in board.game_result and board.game_mode == MODE_HUMAN_VS_AI:
        # Base gold reward
        gold_reward = 50
        
        # Bonus based on AI difficulty
        if board.ai_difficulty <= 5:
            gold_reward += 10
            min_rarity = RPGChessPiece.RARITY_COMMON
            max_rarity = RPGChessPiece.RARITY_UNCOMMON
        elif board.ai_difficulty <= 10:
            gold_reward += 25
            min_rarity = RPGChessPiece.RARITY_COMMON
            max_rarity = RPGChessPiece.RARITY_RARE
        else:
            gold_reward += 50
            min_rarity = RPGChessPiece.RARITY_UNCOMMON
            max_rarity = RPGChessPiece.RARITY_EPIC
        
        # Add gold to inventory
        inventory.add_gold(gold_reward)
        
        # Generate a random piece as reward
        reward_piece = inventory.generate_random_piece(min_rarity, max_rarity)
        
        # Add piece to inventory
        inventory.add_piece(reward_piece)
        
        # Add XP to active pieces
        for piece in inventory.active_pieces:
            # Base XP
            xp_gain = 20
            
            # Bonus based on AI difficulty
            if board.ai_difficulty <= 5:
                xp_gain += 5
            elif board.ai_difficulty <= 10:
                xp_gain += 15
            else:
                xp_gain += 30
                
            piece.add_xp(xp_gain)
        
        # Save inventory after rewards
        inventory.save_inventory()

if __name__ == "__main__":
    main() 