import pygame
import time
import random
from typing import List, Tuple, Optional, Dict, Any

from constants import (
    FPS, BOARD_PX, WINDOW_WIDTH, WINDOW_HEIGHT, SQUARE_SIZE, BLACK,
    MODE_HUMAN_VS_HUMAN, MODE_HUMAN_VS_AI, MODE_CHESS, MODE_DUNGEON,
    TILE_SIZE, screen, create_piece_images, create_tile_images
)
from models.chess_board import ChessBoard
from models.player_inventory import PlayerInventory
from models.chess_piece import RPGChessPiece
from models.dungeon import Dungeon, Enemy, Chest
from models.player import Player
from ui.button import Button
from ui.inventory_ui import InventoryUI
from ui.dungeon_ui import DungeonUI

def main() -> None:
    """Main game loop."""
    clock = pygame.time.Clock()
    
    # Initialize game state
    game_mode = MODE_DUNGEON  # Start in dungeon mode
    
    # Initialize player inventory
    player_inventory = PlayerInventory()
    inventory_ui = InventoryUI(player_inventory)
    show_inventory = False
    
    # Initialize chess board (will be used when combat is triggered)
    chess_board = ChessBoard(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=10)
    piece_images = create_piece_images()
    tile_images = create_tile_images()
    dragging = False
    drag_piece = None
    drag_start_pos = None
    
    # Initialize dungeon
    dungeon_width = 50
    dungeon_height = 50
    dungeon = Dungeon(
        width=dungeon_width,
        height=dungeon_height,
        difficulty=1,
        num_rooms=10,
        min_room_size=5,
        max_room_size=10
    )
    
    # Initialize player
    player_start_pos = dungeon.get_starting_position()
    player = Player(player_start_pos, player_inventory)
    
    # Initialize dungeon UI
    dungeon_ui = DungeonUI(dungeon, player, tile_images)
    
    # Create UI buttons with a better layout
    button_width = 180
    button_height = 40
    button_x = BOARD_PX + (WINDOW_WIDTH - BOARD_PX - button_width) // 2
    button_spacing = 15
    
    # Calculate starting Y position for buttons (positioned at the bottom of the UI panel)
    button_start_y = WINDOW_HEIGHT - (button_height + button_spacing) * 6 - button_spacing
    
    # Create mode buttons for chess mode
    chess_buttons = [
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
    chess_buttons.append(reset_button)
    
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
    chess_buttons.append(inventory_button)
    
    # Add a return to dungeon button (only shown in chess mode)
    return_button = Button(
        button_x, 
        button_start_y - (button_height + button_spacing), 
        button_width, 
        button_height, 
        "Return to Dungeon", 
        color=(50, 150, 100),
        hover_color=(70, 180, 120),
        active_color=(90, 200, 140)
    )
    chess_buttons.append(return_button)
    
    # Set the active button based on current game mode
    if chess_board.game_mode == MODE_HUMAN_VS_HUMAN:
        chess_buttons[0].set_active(True)
    else:
        if chess_board.ai_difficulty <= 5:
            chess_buttons[1].set_active(True)
        elif chess_board.ai_difficulty <= 10:
            chess_buttons[2].set_active(True)
        else:
            chess_buttons[3].set_active(True)
    
    # Variables for combat transition
    current_enemy = None
    combat_result = None
    
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
                        
                # Handle player movement in dungeon mode
                if game_mode == MODE_DUNGEON and not show_inventory:
                    # Set movement key state to pressed
                    if event.key in [pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN, 
                                    pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT]:
                        player.set_movement_key(event.key, True)
                    elif event.key == pygame.K_e:  # Interact
                        interaction_result = player.interact(dungeon)
                        if interaction_result:
                            game_mode, current_enemy = handle_interaction(interaction_result, player, dungeon, dungeon_ui)
            
            elif event.type == pygame.KEYUP:
                # Handle key releases for fluid movement
                if game_mode == MODE_DUNGEON and not show_inventory:
                    if event.key in [pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN, 
                                    pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT]:
                        player.set_movement_key(event.key, False)
                            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_clicked = True
                    if game_mode == MODE_CHESS and not show_inventory and mouse_pos[0] < BOARD_PX and not chess_board.animating:
                        # Chess board interaction
                        row, col = chess_board.get_square_at_pos(event.pos)
                        # Store the starting position for drag and drop
                        if 0 <= row < 8 and 0 <= col < 8:
                            piece = chess_board.board[row][col]
                            if piece and piece.color == chess_board.turn:
                                drag_piece = piece
                                drag_start_pos = (row, col)
                                chess_board.select_piece(row, col)
                                dragging = True
                            else:
                                # Clicking on an empty square or opponent's piece
                                # Try to move the selected piece if one is selected
                                if chess_board.selected_piece:
                                    chess_board.move_piece(row, col, piece_images)
                                    chess_board.selected_piece = None
                                    chess_board.legal_moves = []
                                else:
                                    # Just select the square (might be opponent's piece)
                                    chess_board.select_piece(row, col)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:  # Left mouse button
                    if game_mode == MODE_CHESS and not show_inventory and mouse_pos[0] < BOARD_PX and not chess_board.animating:
                        row, col = chess_board.get_square_at_pos(event.pos)
                        # Only try to move if we're releasing on a different square
                        if drag_start_pos != (row, col):
                            moved = chess_board.move_piece(row, col, piece_images)
                            if not moved:
                                # If the move was invalid, clear selection
                                chess_board.selected_piece = None
                                chess_board.legal_moves = []
                    dragging = False
                    drag_piece = None
                    drag_start_pos = None
        
        # Handle inventory UI if it's shown
        if show_inventory:
            inventory_action = inventory_ui.update(mouse_pos, mouse_clicked)
            if inventory_action == "back":
                show_inventory = False
        elif game_mode == MODE_DUNGEON:
            # Update dungeon UI
            dungeon_action = dungeon_ui.update(mouse_pos, mouse_clicked)
            
            # Handle dungeon UI actions
            if dungeon_action.startswith("interaction_"):
                interaction_index = int(dungeon_action.split("_")[1])
                
                # Handle interaction based on the button index
                if dungeon_ui.interaction_target:
                    if isinstance(dungeon_ui.interaction_target, Enemy):
                        if interaction_index == 0:  # Start Combat button
                            # Initiate combat with the enemy
                            game_mode, current_enemy = handle_interaction(dungeon_ui.interaction_target, player, dungeon, dungeon_ui)
                        elif interaction_index == 1:  # Examine button
                            # Show information about the enemy
                            dungeon_ui.add_message(f"Enemy: {dungeon_ui.interaction_target.enemy_type}, Difficulty: {dungeon_ui.interaction_target.difficulty}")
                    elif isinstance(dungeon_ui.interaction_target, Chest):
                        if interaction_index == 0:  # Open Chest button
                            # Open the chest
                            dungeon_ui.add_message("Opening chest...")
                            # TODO: Implement chest opening logic
                        elif interaction_index == 1:  # Examine button
                            # Show information about the chest
                            dungeon_ui.add_message("A locked chest. It might contain valuable items.")
                    
                    # If the last button (Cancel) was clicked, hide the interaction panel
                    if interaction_index == len(dungeon_ui.interaction_buttons) - 1:
                        dungeon_ui.hide_interaction()
            elif dungeon_action.startswith("move_"):
                # Parse the target coordinates
                parts = dungeon_action.split("_")
                if len(parts) == 3:
                    try:
                        target_x = int(parts[1])
                        target_y = int(parts[2])
                        
                        # Calculate the direction to move
                        player_x, player_y = player.position
                        dx = 0
                        dy = 0
                        
                        # Determine the direction to move (only one step at a time)
                        if target_x > player_x:
                            dx = 1
                        elif target_x < player_x:
                            dx = -1
                        elif target_y > player_y:
                            dy = 1
                        elif target_y < player_y:
                            dy = -1
                        
                        # Move the player
                        if dx != 0 or dy != 0:
                            move_player(player, dungeon, dx, dy, dungeon_ui)
                    except ValueError:
                        pass  # Invalid coordinates
            elif dungeon_action == "interact":
                # Trigger the player's interact method
                interaction_result = player.interact(dungeon)
                if interaction_result:
                    game_mode, current_enemy = handle_interaction(interaction_result, player, dungeon, dungeon_ui)
            elif dungeon_action == "end_turn":
                # End the player's turn (if turn-based mechanics are implemented)
                dungeon_ui.add_message("Turn ended")
            elif dungeon_action == "inventory":
                # Show the inventory
                show_inventory = True
            
            # Update player movement
            player.update_velocity()
            if player.update_position(dungeon):
                # Check for encounters after movement
                check_for_encounters(player, dungeon, dungeon_ui)
            
            # Update dungeon visibility based on player position
            tile_x, tile_y = player.get_tile_position()
            dungeon.update_visibility(tile_x, tile_y, player.vision_range)
            
        elif game_mode == MODE_CHESS:
            # Update chess animations
            chess_board.update_animations()
            
            # Check if AI should make a move after thinking time has elapsed
            if chess_board.thinking and current_time - chess_board.ai_move_start_time >= chess_board.ai_move_duration:
                chess_board.make_ai_move(piece_images)
            
            # Update buttons
            for button in chess_buttons:
                button.update(mouse_pos)
            
            # Handle button clicks
            for i, button in enumerate(chess_buttons):
                if button.is_clicked(mouse_pos, mouse_clicked):
                    # Return to Dungeon button should work even during animations
                    if i == 6:  # Return to Dungeon button
                        game_mode = MODE_DUNGEON
                        # If player won the combat, remove the enemy
                        if chess_board.game_over and "White wins" in chess_board.game_result and current_enemy:
                            # Remove the defeated enemy
                            enemy_x, enemy_y = current_enemy.position
                            dungeon_tile = dungeon.grid[enemy_y][enemy_x]
                            dungeon_tile.entity = None
                            dungeon_ui.add_message(f"Enemy defeated!")
                            
                            # Give rewards
                            _handle_game_rewards(chess_board, player_inventory)
                            
                        current_enemy = None
                    # Other buttons should only work when not animating
                    elif not chess_board.animating:
                        if i == 5:  # Inventory button
                            show_inventory = True
                        else:
                            # Reset active state for all buttons
                            for b in chess_buttons[:5]:  # Only reset game mode buttons
                                b.set_active(False)
                            
                            # Handle chess mode button actions
                            if i == 0:  # Human vs Human
                                button.set_active(True)
                                chess_board.reset_game(game_mode=MODE_HUMAN_VS_HUMAN)
                            elif i == 1:  # Human vs AI (Easy)
                                button.set_active(True)
                                chess_board.reset_game(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=5)
                            elif i == 2:  # Human vs AI (Medium)
                                button.set_active(True)
                                chess_board.reset_game(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=10)
                            elif i == 3:  # Human vs AI (Hard)
                                button.set_active(True)
                                chess_board.reset_game(game_mode=MODE_HUMAN_VS_AI, ai_difficulty=15)
                            elif i == 4:  # Reset Game
                                # Keep the same mode but reset the game
                                chess_board.reset_game()
                                # Reset the active state for the reset button
                                button.set_active(False)
                                # Set the appropriate mode button as active
                                if chess_board.game_mode == MODE_HUMAN_VS_HUMAN:
                                    chess_buttons[0].set_active(True)
                                else:
                                    if chess_board.ai_difficulty <= 5:
                                        chess_buttons[1].set_active(True)
                                    elif chess_board.ai_difficulty <= 10:
                                        chess_buttons[2].set_active(True)
                                    else:
                                        chess_buttons[3].set_active(True)
            
            # Check for game over
            if chess_board.game_over and not chess_board.rewards_given:
                chess_board.rewards_given = True
        
        # Clear the screen
        screen.fill(BLACK)
        
        if show_inventory:
            # Draw inventory UI
            inventory_ui.draw(screen, piece_images)
        elif game_mode == MODE_DUNGEON:
            # Draw dungeon UI
            dungeon_ui.draw(screen)
        else:  # Chess mode
            # Draw the chess board and pieces
            chess_board.draw(screen, piece_images)
            
            # Draw the dragged piece at the mouse position if dragging
            if dragging and drag_piece and not chess_board.animating:
                image = piece_images[drag_piece.get_image_key()]
                # Center the piece on the mouse
                screen.blit(image, (mouse_pos[0] - SQUARE_SIZE // 2, mouse_pos[1] - SQUARE_SIZE // 2))
            
            # Draw buttons
            for button in chess_buttons:
                button.draw(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Save inventory before quitting
    player_inventory.save_inventory()
    
    # Clean up
    if chess_board.ai:
        chess_board.ai.close()
    
    pygame.quit()

def move_player(player: Player, dungeon: Dungeon, dx: int, dy: int, dungeon_ui: DungeonUI) -> None:
    """
    Set the player's movement direction.
    
    Args:
        player: The player to move
        dungeon: The dungeon the player is in
        dx: Change in x position (-1, 0, or 1)
        dy: Change in y position (-1, 0, or 1)
        dungeon_ui: The dungeon UI for displaying messages
    """
    # Clear all movement keys first
    for key in player.movement_keys:
        player.set_movement_key(key, False)
    
    # Set the appropriate movement key based on direction
    if dx == -1:
        player.set_movement_key(pygame.K_a, True)
    elif dx == 1:
        player.set_movement_key(pygame.K_d, True)
    
    if dy == -1:
        player.set_movement_key(pygame.K_w, True)
    elif dy == 1:
        player.set_movement_key(pygame.K_s, True)

def check_for_encounters(player: Player, dungeon: Dungeon, dungeon_ui: DungeonUI) -> Optional[Enemy]:
    """
    Check if the player has encountered an enemy or interactive object.
    
    Args:
        player: The player
        dungeon: The dungeon
        dungeon_ui: The dungeon UI for displaying messages
        
    Returns:
        The enemy encountered, if any
    """
    x, y = player.get_tile_position()
    
    # Check adjacent tiles for enemies
    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
        check_x, check_y = x + dx, y + dy
        
        if 0 <= check_x < dungeon.width and 0 <= check_y < dungeon.height:
            entity = dungeon.get_entity_at(check_x, check_y)
            
            if isinstance(entity, Enemy):
                dungeon_ui.add_message(f"Enemy encountered! Prepare for battle!")
                dungeon_ui.show_interaction(entity)
                return entity
    
    return None

def handle_interaction(interaction_result: Any, player: Player, dungeon: Dungeon, dungeon_ui: DungeonUI) -> Tuple[str, Optional[Enemy]]:
    """
    Handle the result of a player interaction.
    
    Args:
        interaction_result: The result of the interaction
        player: The player
        dungeon: The dungeon
        dungeon_ui: The dungeon UI
        
    Returns:
        A tuple of (new_game_mode, new_current_enemy)
    """
    new_game_mode = MODE_DUNGEON
    new_current_enemy = None
    
    if isinstance(interaction_result, Enemy):
        dungeon_ui.add_message(f"Engaging enemy in combat!")
        # Combat will be initiated in the main loop
        new_game_mode = MODE_CHESS
        new_current_enemy = interaction_result
    elif isinstance(interaction_result, str):
        dungeon_ui.add_message(interaction_result)
    
    return new_game_mode, new_current_enemy

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