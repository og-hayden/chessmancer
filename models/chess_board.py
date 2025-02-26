import pygame
import time
import numpy as np
import math
from typing import List, Tuple, Dict, Optional, Set

from constants import (
    BOARD_SIZE, SQUARE_SIZE, BOARD_PX, WINDOW_WIDTH, WINDOW_HEIGHT,
    LIGHT_SQUARE, DARK_SQUARE, BOARD_BORDER, HIGHLIGHT, SELECTED, LAST_MOVE,
    WHITE_PIECE, BLACK_PIECE, UI_BG, UI_PANEL_BORDER, UI_TEXT, UI_HEADING, UI_SECTION_BG,
    PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    MODE_HUMAN_VS_HUMAN, MODE_HUMAN_VS_AI,
    MIN_AI_MOVE_TIME, MAX_AI_MOVE_TIME
)
from models.chess_piece import ChessPiece
from ui.animations import AnimatedPiece
from chess_ai import ChessAI

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
                # Get all potential legal moves
                potential_moves = piece.get_legal_moves(self)
                # Filter out moves that would leave the king in check
                self.legal_moves = self.filter_legal_moves_for_check(piece, potential_moves)
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
            
            # Check if the opponent's king is in check
            opponent_color = 'black' if self.turn == 'white' else 'white'
            if self.is_king_in_check(opponent_color):
                # Check if it's checkmate
                if self.is_checkmate(opponent_color):
                    self.game_over = True
                    winner = 'white' if opponent_color == 'black' else 'black'
                    self.game_result = f"Checkmate! {winner.capitalize()} wins."
            
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
    
    def find_king(self, color: str) -> Optional[Tuple[int, int]]:
        """Find the position of the king of the specified color."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.piece_type == KING and piece.color == color:
                    return (row, col)
        return None
    
    def is_square_attacked(self, row: int, col: int, by_color: str) -> bool:
        """Check if a square is attacked by any piece of the specified color."""
        # Check for attacks from pawns
        pawn_direction = 1 if by_color == 'black' else -1
        for dc in [-1, 1]:
            attack_row = row + pawn_direction
            attack_col = col + dc
            if 0 <= attack_row < BOARD_SIZE and 0 <= attack_col < BOARD_SIZE:
                piece = self.board[attack_row][attack_col]
                if piece and piece.piece_type == PAWN and piece.color == by_color:
                    return True
        
        # Check for attacks from knights
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_moves:
            attack_row, attack_col = row + dr, col + dc
            if 0 <= attack_row < BOARD_SIZE and 0 <= attack_col < BOARD_SIZE:
                piece = self.board[attack_row][attack_col]
                if piece and piece.piece_type == KNIGHT and piece.color == by_color:
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
                piece = self.board[attack_row][attack_col]
                if piece and piece.piece_type == KING and piece.color == by_color:
                    return True
        
        # Check diagonal attacks (bishop, queen)
        diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diagonals:
            for i in range(1, BOARD_SIZE):
                attack_row, attack_col = row + i * dr, col + i * dc
                
                if not (0 <= attack_row < BOARD_SIZE and 0 <= attack_col < BOARD_SIZE):
                    break
                
                piece = self.board[attack_row][attack_col]
                if piece:
                    if piece.color == by_color and (piece.piece_type == BISHOP or piece.piece_type == QUEEN):
                        # Verify it's a valid diagonal attack
                        if abs(row - attack_row) == abs(col - attack_col):
                            return True
                    break  # Stop if we hit any piece
        
        # Check orthogonal attacks (rook, queen)
        orthogonals = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in orthogonals:
            for i in range(1, BOARD_SIZE):
                attack_row, attack_col = row + i * dr, col + i * dc
                
                if not (0 <= attack_row < BOARD_SIZE and 0 <= attack_col < BOARD_SIZE):
                    break
                
                piece = self.board[attack_row][attack_col]
                if piece:
                    if piece.color == by_color and (piece.piece_type == ROOK or piece.piece_type == QUEEN):
                        # Verify it's a valid orthogonal attack
                        if row == attack_row or col == attack_col:
                            return True
                    break  # Stop if we hit any piece
        
        return False
    
    def is_king_in_check(self, color: str) -> bool:
        """Check if the king of the specified color is in check."""
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        
        row, col = king_pos
        opponent_color = 'black' if color == 'white' else 'white'
        return self.is_square_attacked(row, col, opponent_color)
    
    def would_move_cause_check(self, piece: ChessPiece, to_row: int, to_col: int) -> bool:
        """Check if moving a piece to a position would cause the king to be in check."""
        # Save the current state
        from_row, from_col = piece.position
        captured_piece = self.board[to_row][to_col]
        
        # Make the move temporarily
        self.board[from_row][from_col] = None
        self.board[to_row][to_col] = piece
        piece.position = (to_row, to_col)
        
        # Check if the king is in check
        king_in_check = self.is_king_in_check(piece.color)
        
        # Restore the board state
        piece.position = (from_row, from_col)
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured_piece
        
        return king_in_check
    
    def filter_legal_moves_for_check(self, piece: ChessPiece, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Filter out moves that would leave the king in check."""
        legal_moves = []
        for move in moves:
            to_row, to_col = move
            if not self.would_move_cause_check(piece, to_row, to_col):
                legal_moves.append(move)
        return legal_moves
    
    def is_checkmate(self, color: str) -> bool:
        """Check if the king of the specified color is in checkmate."""
        # If the king is not in check, it's not checkmate
        if not self.is_king_in_check(color):
            return False
        
        # Check if any piece can make a move that gets the king out of check
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    # Get all potential legal moves
                    potential_moves = piece.get_legal_moves(self)
                    # Filter out moves that would leave the king in check
                    legal_moves = self.filter_legal_moves_for_check(piece, potential_moves)
                    if legal_moves:
                        return False
        
        # If no piece can make a legal move, it's checkmate
        return True
    
    def clear_board(self):
        """Clear all pieces from the board."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.board[row][col] = None 