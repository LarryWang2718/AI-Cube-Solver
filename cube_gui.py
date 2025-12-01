"""
GUI for Rubik's Cube Solver with visualization.

Shows a 2D net view of the cube, allows color selection, and animates solving steps.
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import numpy as np
from cube_state import CubeState, solved_state
from moves import MOVE_TABLE
from heuristics import Heuristic
from search import IDAStar
import threading
import time
import subprocess
import sys
import os
import re


# Standard Rubik's Cube colors (RGB)
STANDARD_COLORS = {
    'W': '#FFFFFF',  # White
    'Y': '#FFFF00',  # Yellow
    'R': '#FF0000',  # Red
    'O': '#FF8800',  # Orange
    'B': '#0000FF',  # Blue
    'G': '#00FF00',  # Green
}

# Face mapping for 2D net view
# Net layout:
#     U
#   L F R B
#     D
FACE_NAMES = ['U', 'L', 'F', 'R', 'B', 'D']  # Up, Left, Front, Right, Back, Down


class CubeVisualizer:
    """Visualizes a Rubik's cube in 2D net format."""
    
    def __init__(self, canvas, cell_size=40, spacing=5):
        """
        Initialize visualizer.
        
        Args:
            canvas: tkinter Canvas widget
            cell_size: size of each facelet (default 40)
            spacing: spacing between faces (default 5)
        """
        self.canvas = canvas
        self.cell_size = cell_size
        self.spacing = spacing
        
        # Cube state as 6 faces, each 3x3
        # faces[face_index][row][col] = color_code
        self.faces = np.zeros((6, 3, 3), dtype=int)
        self._initialize_solved_state()
        
        # Color mapping: 0=W, 1=Y, 2=R, 3=O, 4=B, 5=G
        self.color_codes = ['W', 'Y', 'R', 'O', 'B', 'G']
        self.color_values = [STANDARD_COLORS[c] for c in self.color_codes]
        
        # Face positions in net (row, col)
        self.face_positions = {
            0: (0, 1),  # U (Up)
            1: (1, 0),  # L (Left)
            2: (1, 1),  # F (Front)
            3: (1, 2),  # R (Right)
            4: (1, 3),  # B (Back)
            5: (2, 1),  # D (Down)
        }
    
    def _initialize_solved_state(self):
        """Initialize to solved state using the converter."""
        from cube_state import solved_state
        from cube_converter import cubie_state_to_faces
        solved = solved_state()
        self.faces = cubie_state_to_faces(solved)
    
    def get_facelet_color(self, face_idx, row, col):
        """Get color code for a facelet."""
        return int(self.faces[face_idx, row, col])
    
    def set_facelet_color(self, face_idx, row, col, color_code):
        """Set color for a facelet."""
        self.faces[face_idx, row, col] = color_code
    
    def set_face_color(self, face_idx, color_code):
        """Set entire face to one color."""
        self.faces[face_idx].fill(color_code)
    
    def draw(self):
        """Draw the cube net on the canvas."""
        self.canvas.delete("all")
        
        for face_idx in range(6):
            row_pos, col_pos = self.face_positions[face_idx]
            x_start = col_pos * (3 * self.cell_size + self.spacing) + self.spacing
            y_start = row_pos * (3 * self.cell_size + self.spacing) + self.spacing
            
            # Draw face label
            face_name = FACE_NAMES[face_idx]
            self.canvas.create_text(
                x_start + 1.5 * self.cell_size,
                y_start - 15,
                text=face_name,
                font=('Arial', 10, 'bold')
            )
            
            # Draw 3x3 grid of facelets
            for row in range(3):
                for col in range(3):
                    x = x_start + col * self.cell_size
                    y = y_start + row * self.cell_size
                    
                    color_code = self.get_facelet_color(face_idx, row, col)
                    color = self.color_values[color_code]
                    
                    # Draw rectangle with border
                    self.canvas.create_rectangle(
                        x, y,
                        x + self.cell_size, y + self.cell_size,
                        fill=color,
                        outline='black',
                        width=2,
                        tags=f"facelet_{face_idx}_{row}_{col}"
                    )
    
    def get_facelet_at_position(self, x, y):
        """Get facelet coordinates from canvas position."""
        for face_idx in range(6):
            row_pos, col_pos = self.face_positions[face_idx]
            x_start = col_pos * (3 * self.cell_size + self.spacing) + self.spacing
            y_start = row_pos * (3 * self.cell_size + self.spacing) + self.spacing
            
            if x_start <= x < x_start + 3 * self.cell_size:
                if y_start <= y < y_start + 3 * self.cell_size:
                    col = int((x - x_start) / self.cell_size)
                    row = int((y - y_start) / self.cell_size)
                    if 0 <= row < 3 and 0 <= col < 3:
                        return (face_idx, row, col)
        return None
    
    def apply_move(self, move_name):
        """Apply a move to the visual representation."""
        state = self.to_cube_state()
        if state is None:
            print(f"Warning: Cannot apply move {move_name} - invalid cube state")
            return False
        
        if move_name in MOVE_TABLE:
            new_state = MOVE_TABLE[move_name].apply(state)
            self.from_cube_state(new_state)
            return True
        return False
    
    def to_cube_state(self):
        """Convert visual representation to cubie model."""
        try:
            from cube_converter import faces_to_cubie_state
            return faces_to_cubie_state(self.faces)
        except Exception as e:
            print(f"Error converting to cubie state: {e}")
            return None
    
    def from_cube_state(self, state: CubeState):
        """Convert cubie model to visual representation."""
        try:
            from cube_converter import cubie_state_to_faces
            self.faces = cubie_state_to_faces(state)
            self.draw()
        except Exception as e:
            print(f"Error converting from cubie state: {e}")


class ColorPicker:
    """Color picker widget for selecting cube face colors."""
    
    def __init__(self, parent):
        self.parent = parent
        self.selected_color = 0  # Default to white
        
        # Create color buttons
        frame = ttk.Frame(parent)
        frame.pack(pady=10)
        
        ttk.Label(frame, text="Select Color:").pack(side=tk.LEFT, padx=5)
        
        self.color_buttons = []
        for i, (code, color) in enumerate(STANDARD_COLORS.items()):
            btn = tk.Button(
                frame,
                text=code,
                bg=color,
                width=3,
                height=1,
                command=lambda c=i: self.set_color(c),
                relief=tk.RAISED if i == 0 else tk.FLAT
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.color_buttons.append(btn)
    
    def set_color(self, color_code):
        """Set selected color and update button appearance."""
        self.selected_color = color_code
        for i, btn in enumerate(self.color_buttons):
            btn.config(relief=tk.RAISED if i == color_code else tk.FLAT)
    
    def get_color(self):
        """Get currently selected color code."""
        return self.selected_color


class CubeSolverGUI:
    """Main GUI application for cube solver."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Rubik's Cube Solver - Visual Interface")
        self.root.geometry("800x700")
        
        # Initialize components
        self.heuristic = None
        self.solver = None
        self.solution = None
        self.solving = False
        self.current_scramble = None  # Store the current scramble string
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Rubik's Cube Solver",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=10)
        
        # Canvas for cube visualization
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=600,
            height=400,
            bg='white',
            borderwidth=2,
            relief=tk.SUNKEN
        )
        self.canvas.pack()
        
        # Initialize visualizer
        self.visualizer = CubeVisualizer(self.canvas, cell_size=35, spacing=8)
        self.visualizer.draw()
        
        # Color picker
        self.color_picker = ColorPicker(main_frame)
        
        # Instructions
        instructions_frame = ttk.Frame(main_frame)
        instructions_frame.pack(pady=5)
        
        instructions1 = ttk.Label(
            instructions_frame,
            text="Layout: [U] on top, [L][F][R][B] in middle, [D] on bottom",
            font=('Arial', 9, 'bold'),
            foreground='darkblue'
        )
        instructions1.pack()
        
        instructions2 = ttk.Label(
            instructions_frame,
            text="Click facelets to change color, or use 'Load from Scramble' (recommended)",
            font=('Arial', 9),
            foreground='gray'
        )
        instructions2.pack()
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame,
            text="Reset to Solved",
            command=self.reset_cube
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Load from Scramble",
            command=self.load_from_scramble
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Solve",
            command=self.solve_cube
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Animate Solution",
            command=self.animate_solution
        ).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Ready",
            font=('Arial', 10)
        )
        self.status_label.pack(pady=5)
        
        # Solution display
        self.solution_text = tk.Text(
            main_frame,
            height=3,
            width=60,
            wrap=tk.WORD
        )
        self.solution_text.pack(pady=5)
        
        # Bind canvas click
        self.canvas.bind("<Button-1>", self.on_canvas_click)
    
    def on_canvas_click(self, event):
        """Handle click on canvas to change facelet color."""
        facelet = self.visualizer.get_facelet_at_position(event.x, event.y)
        if facelet:
            face_idx, row, col = facelet
            color_code = self.color_picker.get_color()
            self.visualizer.set_facelet_color(face_idx, row, col, color_code)
            self.visualizer.draw()
    
    def reset_cube(self):
        """Reset cube to solved state."""
        from cube_state import solved_state
        from cube_converter import cubie_state_to_faces
        solved = solved_state()
        self.visualizer.faces = cubie_state_to_faces(solved)
        self.visualizer.draw()
        self.current_scramble = None  # Clear stored scramble
        self.status_label.config(text="Cube reset to solved state")
        self.solution_text.delete(1.0, tk.END)
    
    def load_from_scramble(self):
        """Load cube state from a scramble string."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Scramble")
        dialog.geometry("400x150")
        
        ttk.Label(
            dialog,
            text="Enter scramble moves (e.g., 'U R F2 D L'):"
        ).pack(pady=10)
        
        entry = ttk.Entry(dialog, width=40)
        entry.pack(pady=5)
        entry.focus()
        
        def apply_scramble():
            scramble_str = entry.get().strip()
            if scramble_str:
                try:
                    from utils import apply_moves
                    state = solved_state()
                    moves = scramble_str.split()
                    scrambled = apply_moves(state, moves)
                    # Update visualizer
                    self.visualizer.from_cube_state(scrambled)
                    # Store the scramble string for later use in solving
                    self.current_scramble = scramble_str
                    self.status_label.config(text=f"Scramble applied: {scramble_str}")
                    self.solution = None
                    self.solution_text.delete(1.0, tk.END)
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid scramble: {e}")
            dialog.destroy()
        
        ttk.Button(dialog, text="Apply", command=apply_scramble).pack(pady=10)
        dialog.bind('<Return>', lambda e: apply_scramble())
    
    def solve_cube(self):
        """Solve the cube using command-line interface."""
        if self.solving:
            messagebox.showwarning("Warning", "Solver is already running!")
            return
        
        # Check if we have a stored scramble
        if self.current_scramble is None:
            messagebox.showwarning(
                "No Scramble",
                "Please use 'Load from Scramble' first to input a scramble.\n\n"
                "Solving from manually edited cube colors is not supported."
            )
            return
        
        # Solve in background thread using command-line interface
        self.solving = True
        self.status_label.config(text="Solving... Please wait...")
        self.root.update()
        
        def solve_thread():
            try:
                self.status_label.config(text="Calling solver...")
                self.root.update()
                
                # Get the directory of the current script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                main_py = os.path.join(script_dir, "main.py")
                
                # Build command: python main.py --moves "scramble"
                cmd = [sys.executable, main_py, "--moves", self.current_scramble, "--max-iterations", "50"]
                
                # Run the command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=script_dir,
                    timeout=300  # 5 minute timeout
                )
                
                # Parse output to extract solution
                output = result.stdout
                solution = None
                nodes_expanded = None
                elapsed_time = None
                
                # Look for solution line: "Solution found (N moves):" followed by indented moves
                # Format: "Solution found (2 moves):\n  R' U'"
                solution_match = re.search(r'Solution found \((\d+) moves\):\s*\n\s+([^\n]+)', output)
                if solution_match:
                    num_moves = int(solution_match.group(1))
                    solution_str = solution_match.group(2).strip()
                    # Split by whitespace to get individual moves
                    solution = solution_str.split()
                
                # Look for statistics
                nodes_match = re.search(r'Nodes expanded:\s*([\d,]+)', output)
                if nodes_match:
                    nodes_expanded = nodes_match.group(1).replace(',', '')
                
                time_match = re.search(r'Time:\s*([\d.]+)\s*seconds', output)
                if time_match:
                    elapsed_time = float(time_match.group(1))
                
                # Check for errors
                if result.returncode != 0 or "No solution found" in output:
                    self.solution = None
                    self.solution_text.delete(1.0, tk.END)
                    self.solution_text.insert(1.0, "No solution found within limits.")
                    self.status_label.config(text="No solution found")
                    messagebox.showwarning("Warning", "No solution found within iteration limit.")
                    return
                
                if solution:
                    self.solution = solution
                    solution_str = " ".join(solution)
                    stats_text = f"Solution ({len(solution)} moves): {solution_str}"
                    if nodes_expanded:
                        stats_text += f"\nNodes expanded: {nodes_expanded}"
                    if elapsed_time:
                        stats_text += f" | Time: {elapsed_time:.2f}s"
                    self.solution_text.delete(1.0, tk.END)
                    self.solution_text.insert(1.0, stats_text)
                    self.status_label.config(text=f"Solution found! {len(solution)} moves")
                else:
                    # Fallback: try to extract from output even if regex didn't match
                    self.solution = None
                    self.solution_text.delete(1.0, tk.END)
                    self.solution_text.insert(1.0, "Could not parse solution from output.\n\n" + output[-500:])
                    self.status_label.config(text="Error parsing solution")
                    messagebox.showerror("Error", "Could not parse solution from solver output.")
                    
            except subprocess.TimeoutExpired:
                messagebox.showerror("Error", "Solver timed out after 5 minutes.")
                self.status_label.config(text="Solver timed out")
            except Exception as e:
                messagebox.showerror("Error", f"Error during solving: {e}")
                self.status_label.config(text="Error during solving")
            finally:
                self.solving = False
        
        thread = threading.Thread(target=solve_thread, daemon=True)
        thread.start()
    
    def animate_solution(self):
        """Animate the solution steps."""
        if not self.solution:
            messagebox.showwarning("Warning", "No solution available. Solve the cube first.")
            return
        
        # Check if we have a scramble to recreate the initial state
        if not self.current_scramble:
            messagebox.showwarning(
                "Warning", 
                "Cannot animate: no scramble stored.\n"
                "Please use 'Load from Scramble' first, then solve."
            )
            return
        
        self.status_label.config(text="Animating solution...")
        
        # Recreate the scrambled state from the stored scramble string
        # This ensures we start from the exact same state the solution was computed for
        try:
            from utils import apply_moves
            # Start from solved state
            current_state = solved_state()
            # Apply the scramble moves to recreate the initial scrambled state
            scramble_moves = self.current_scramble.split()
            current_state = apply_moves(current_state, scramble_moves)
            
            # Update visualizer to show the scrambled state first
            self.visualizer.from_cube_state(current_state)
            self.root.update()
            time.sleep(0.5)  # Brief pause before starting solution
            
        except Exception as e:
            messagebox.showerror("Error", f"Error recreating scrambled state: {e}")
            return
        
        # Animate each move in the solution
        for i, move_name in enumerate(self.solution):
            if move_name in MOVE_TABLE:
                # Apply the move to the state
                current_state = MOVE_TABLE[move_name].apply(current_state)
                # Update visualizer
                self.visualizer.from_cube_state(current_state)
                self.status_label.config(text=f"Animating solution... Move {i+1}/{len(self.solution)}: {move_name}")
                self.root.update()
                time.sleep(0.8)  # Delay between moves
        
        # Verify final state
        if current_state.is_solved():
            self.status_label.config(text="Animation complete! Cube is solved!")
            messagebox.showinfo("Success", "Solution animation complete! Cube is solved!")
        else:
            self.status_label.config(text="Animation complete (but cube may not be solved)")
            messagebox.showwarning("Warning", "Animation complete, but cube state may be incorrect.")


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = CubeSolverGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

