import chess
import chess.engine
import os
import platform
from typing import Tuple, Optional, List
import subprocess
import time

class ChessAI:
    """A chess AI that uses the Stockfish chess engine to make moves."""
    
    def __init__(self, difficulty: int = 10, time_limit: float = 0.1):
        """
        Initialize the chess AI.
        
        Args:
            difficulty: The difficulty level (1-20), higher is stronger
            time_limit: Time limit for engine analysis in seconds
        """
        self.difficulty = min(max(difficulty, 1), 20)  # Clamp between 1 and 20
        self.time_limit = time_limit
        self.engine = None
        self.board = chess.Board()
        
        # Try to find Stockfish executable
        self.stockfish_path = self._find_stockfish()
        if not self.stockfish_path:
            print("Stockfish not found. Downloading Stockfish...")
            self.stockfish_path = self._download_stockfish()
        
        if self.stockfish_path:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
                # Set engine options based on difficulty
                self.engine.configure({"Skill Level": self.difficulty})
                print(f"Stockfish engine loaded successfully at {self.stockfish_path}")
            except Exception as e:
                print(f"Error initializing Stockfish engine: {e}")
                self.engine = None
        else:
            print("Could not find or download Stockfish. AI will use random moves.")
    
    def _find_stockfish(self) -> Optional[str]:
        """Try to find the Stockfish executable on the system."""
        # Check if Stockfish is in the current directory
        system = platform.system()
        
        # Define possible executable names based on OS
        if system == "Windows":
            executable_names = ["stockfish.exe", "stockfish-windows-x86-64.exe", "stockfish-windows-2022-x86-64-avx2.exe"]
        elif system == "Darwin":  # macOS
            executable_names = ["stockfish", "stockfish-macos-x86-64", "stockfish-macos-arm64"]
        else:  # Linux and others
            executable_names = ["stockfish", "stockfish-ubuntu-x86-64", "stockfish-ubuntu-20.04-x86-64"]
        
        # Check current directory
        for name in executable_names:
            if os.path.exists(name) and os.access(name, os.X_OK):
                return os.path.abspath(name)
        
        # Check if Stockfish is in PATH
        try:
            if system == "Windows":
                # On Windows, check if stockfish is in PATH
                result = subprocess.run(["where", "stockfish"], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip().split("\n")[0]
            else:
                # On Unix-like systems, use which
                result = subprocess.run(["which", "stockfish"], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception:
            pass
        
        return None
    
    def _download_stockfish(self) -> Optional[str]:
        """Download the appropriate Stockfish binary for the current platform."""
        import urllib.request
        import zipfile
        import tarfile
        import shutil
        
        system = platform.system()
        machine = platform.machine().lower()
        
        # Define download URLs and binary names based on platform
        if system == "Windows":
            if "amd64" in machine or "x86_64" in machine:
                # For Windows with x86_64 architecture
                url = "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-windows-x86-64-avx2.zip"
                zip_file = "stockfish.zip"
                binary_name = "stockfish-windows-x86-64-avx2.exe"
                final_name = "stockfish.exe"
            else:
                print(f"Unsupported Windows architecture: {machine}")
                return None
        elif system == "Darwin":  # macOS
            if "arm64" in machine:
                # For Apple Silicon
                url = "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-macos-x86-64-modern.tar.gz"
                zip_file = "stockfish.tar.gz"
                binary_name = "stockfish-macos-x86-64-modern"
                final_name = "stockfish"
            else:
                # For Intel Macs
                url = "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-macos-x86-64-modern.tar.gz"
                zip_file = "stockfish.tar.gz"
                binary_name = "stockfish-macos-x86-64-modern"
                final_name = "stockfish"
        elif system == "Linux":
            # For Linux
            url = "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-ubuntu-x86-64-avx2.tar.gz"
            zip_file = "stockfish.tar.gz"
            binary_name = "stockfish-ubuntu-x86-64-avx2"
            final_name = "stockfish"
        else:
            print(f"Unsupported operating system: {system}")
            return None
        
        try:
            # Download the file
            print(f"Downloading Stockfish from {url}...")
            urllib.request.urlretrieve(url, zip_file)
            
            # Extract the file
            if zip_file.endswith(".zip"):
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall("stockfish_temp")
            elif zip_file.endswith(".tar.gz"):
                with tarfile.open(zip_file, 'r:gz') as tar_ref:
                    tar_ref.extractall("stockfish_temp")
            
            # Find the binary
            stockfish_path = None
            for root, dirs, files in os.walk("stockfish_temp"):
                for file in files:
                    if binary_name in file:
                        stockfish_path = os.path.join(root, file)
                        break
                if stockfish_path:
                    break
            
            if not stockfish_path:
                print("Could not find Stockfish binary in the downloaded package.")
                return None
            
            # Copy to final location and make executable
            shutil.copy(stockfish_path, final_name)
            os.chmod(final_name, 0o755)  # Make executable
            
            # Clean up
            if os.path.exists(zip_file):
                os.remove(zip_file)
            if os.path.exists("stockfish_temp"):
                shutil.rmtree("stockfish_temp")
            
            return os.path.abspath(final_name)
        
        except Exception as e:
            print(f"Error downloading Stockfish: {e}")
            return None
    
    def update_board(self, moves: List[Tuple[Tuple[int, int], Tuple[int, int]]]) -> None:
        """
        Update the internal chess board with the moves made in the game.
        
        Args:
            moves: List of moves as ((from_row, from_col), (to_row, to_col))
        """
        # Reset the board
        self.board = chess.Board()
        
        # Apply all moves
        for i, (from_pos, to_pos) in enumerate(moves):
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            # Convert to chess notation (e.g., e2e4)
            from_square = chess.square(from_col, 7 - from_row)  # Flip row because chess.py uses 0 for bottom row
            to_square = chess.square(to_col, 7 - to_row)
            
            # Check if it's a castling move
            is_castling = False
            piece = self.board.piece_at(from_square)
            if piece and piece.piece_type == chess.KING:
                # Kingside castling
                if from_col == 4 and to_col == 6:
                    # Try to find the castling move in legal moves
                    for legal_move in self.board.legal_moves:
                        if (legal_move.from_square == from_square and 
                            legal_move.to_square == to_square and 
                            self.board.is_castling(legal_move)):
                            self.board.push(legal_move)
                            is_castling = True
                            break
                # Queenside castling
                elif from_col == 4 and to_col == 2:
                    # Try to find the castling move in legal moves
                    for legal_move in self.board.legal_moves:
                        if (legal_move.from_square == from_square and 
                            legal_move.to_square == to_square and 
                            self.board.is_castling(legal_move)):
                            self.board.push(legal_move)
                            is_castling = True
                            break
            
            if is_castling:
                continue
            
            # Check for en passant
            is_en_passant = False
            if piece and piece.piece_type == chess.PAWN:
                # Check if it's a diagonal move to an empty square (characteristic of en passant)
                if from_col != to_col and self.board.piece_at(to_square) is None:
                    # Try to find the en passant move in legal moves
                    for legal_move in self.board.legal_moves:
                        if (legal_move.from_square == from_square and 
                            legal_move.to_square == to_square and 
                            self.board.is_en_passant(legal_move)):
                            self.board.push(legal_move)
                            is_en_passant = True
                            break
            
            if is_en_passant:
                continue
            
            # Create the move
            move = chess.Move(from_square, to_square)
            
            # Check if it's a promotion
            if self.board.piece_at(from_square) and self.board.piece_at(from_square).piece_type == chess.PAWN:
                if to_row == 0 or to_row == 7:  # Promotion rank
                    move = chess.Move(from_square, to_square, promotion=chess.QUEEN)
            
            # Apply the move
            if move in self.board.legal_moves:
                self.board.push(move)
            else:
                print(f"Warning: Illegal move {move} not applied to AI's board")
                # Try to find a similar legal move
                for legal_move in self.board.legal_moves:
                    if legal_move.from_square == from_square and legal_move.to_square == to_square:
                        self.board.push(legal_move)
                        print(f"Applied similar legal move {legal_move} instead")
                        break
    
    def get_best_move(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Get the best move according to the engine.
        
        Returns:
            A tuple ((from_row, from_col), (to_row, to_col)) or None if no move is found
        """
        if not self.engine:
            return self._get_random_move()
        
        try:
            # Get the best move from the engine
            result = self.engine.play(
                self.board, 
                chess.engine.Limit(time=self.time_limit)
            )
            
            move = result.move
            if not move:
                return None
            
            # Convert from chess.py notation to our board coordinates
            from_square = move.from_square
            to_square = move.to_square
            
            from_col = chess.square_file(from_square)
            from_row = 7 - chess.square_rank(from_square)  # Flip row because chess.py uses 0 for bottom row
            
            to_col = chess.square_file(to_square)
            to_row = 7 - chess.square_rank(to_square)
            
            # Apply the move to the internal board
            self.board.push(move)
            
            return ((from_row, from_col), (to_row, to_col))
        
        except Exception as e:
            print(f"Error getting move from engine: {e}")
            return self._get_random_move()
    
    def _get_random_move(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get a random legal move if the engine is not available."""
        if self.board.is_game_over():
            return None
        
        # Get a random legal move
        try:
            import random
            legal_moves = list(self.board.legal_moves)
            if not legal_moves:
                return None
            
            move = random.choice(legal_moves)
            
            # Convert from chess.py notation to our board coordinates
            from_square = move.from_square
            to_square = move.to_square
            
            from_col = chess.square_file(from_square)
            from_row = 7 - chess.square_rank(from_square)
            
            to_col = chess.square_file(to_square)
            to_row = 7 - chess.square_rank(to_square)
            
            # Apply the move to the internal board
            self.board.push(move)
            
            return ((from_row, from_col), (to_row, to_col))
        
        except Exception as e:
            print(f"Error getting random move: {e}")
            return None
    
    def is_game_over(self) -> bool:
        """Check if the game is over according to chess rules."""
        return self.board.is_game_over()
    
    def get_game_result(self) -> str:
        """Get the result of the game if it's over."""
        if not self.is_game_over():
            return "Game in progress"
        
        if self.board.is_checkmate():
            return "Checkmate"
        elif self.board.is_stalemate():
            return "Stalemate"
        elif self.board.is_insufficient_material():
            return "Draw (insufficient material)"
        elif self.board.is_fifty_moves():
            return "Draw (fifty-move rule)"
        elif self.board.is_repetition():
            return "Draw (threefold repetition)"
        else:
            return "Draw"
    
    def close(self) -> None:
        """Close the engine properly."""
        if self.engine:
            self.engine.quit()
            self.engine = None

# Test the AI
if __name__ == "__main__":
    ai = ChessAI(difficulty=10)
    
    # Make a few moves to test
    moves = []
    
    # Make 5 moves
    for _ in range(5):
        move = ai.get_best_move()
        if move:
            print(f"AI suggests move: {move}")
            moves.append(move)
        else:
            print("No move found or game over")
            break
    
    ai.close() 