"""
Modern Game Board UI - Giao diện bàn cờ hiện đại
Improved Five-in-a-Row game board interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math

class GameBoardUI:
    """Modern game board interface with improved graphics"""
    
    def __init__(self, parent, size=15, cell_size=30):
        self.parent = parent
        self.size = size
        self.cell_size = cell_size
        self.margin = 40
        
        # Colors
        self.board_color = "#FFFFFF"  # White
        self.line_color = "#8B4513"   # SaddleBrown
        self.player1_color = "#000000"  # Black
        self.player2_color = "#FFFFFF"  # White
        self.highlight_color = "#FFD700"  # Gold
        self.last_move_color = "#FF6B6B"  # Light red
        
        # Game state
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.last_move = None
        self.current_player = 1
        self.game_enabled = True
        self.move_callback = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the game board user interface"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Game info frame
        self.info_frame = ttk.Frame(self.main_frame)
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Canvas for game board
        canvas_size = self.size * self.cell_size + 2 * self.margin
        self.canvas = tk.Canvas(
            self.main_frame,
            width=canvas_size,
            height=canvas_size,
            bg=self.board_color,
            highlightthickness=0,
            highlightbackground="#8B4513"
        )
        self.canvas.pack(expand=True)
        
        # Draw initial board
        self.draw_board()
    
    def draw_board(self):
        """Draw the game board grid"""
        self.canvas.delete("all")
        
        # Draw background
        self.canvas.create_rectangle(
            0, 0, 
            self.size * self.cell_size + 2 * self.margin,
            self.size * self.cell_size + 2 * self.margin,
            fill=self.board_color,
            outline=""
        )
        
        # Draw grid lines
        for i in range(self.size):
            # Vertical lines
            x = self.margin + i * self.cell_size
            self.canvas.create_line(
                x, self.margin,
                x, self.margin + (self.size - 1) * self.cell_size,
                fill=self.line_color,
                width=1
            )
            
            # Horizontal lines
            y = self.margin + i * self.cell_size
            self.canvas.create_line(
                self.margin, y,
                self.margin + (self.size - 1) * self.cell_size, y,
                fill=self.line_color,
                width=1
            )

# Demo application
class GameBoardDemo:
    """Demo application to showcase the game board"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Five in a Row - Modern Game Board")
        self.root.geometry("600x700")
        
        # Apply modern theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create game board
        self.game_board = GameBoardUI(self.root, size=20, cell_size=25)
            
    def run(self):
        """Run the demo application"""
        self.root.mainloop()