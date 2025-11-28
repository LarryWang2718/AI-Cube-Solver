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
                    self.status_label.config(text=f"Scramble applied: {scramble_str}")
                    self.solution = None
                    self.solution_text.delete(1.0, tk.END)
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid scramble: {e}")
            dialog.destroy()
        
        ttk.Button(dialog, text="Apply", command=apply_scramble).pack(pady=10)
        dialog.bind('<Return>', lambda e: apply_scramble())
    
    def solve_cube(self):
        """Solve the cube."""
        if self.solving:
            messagebox.showwarning("Warning", "Solver is already running!")
            return
        
        # Convert visual state to cubie model
        try:
            state = self.visualizer.to_cube_state()
            if state is None:
                messagebox.showerror(
                    "Cannot Resolve Cube State",
                    "Could not convert the visual cube to a valid state.\n\n"
                    "This usually happens when:\n"
                    "• Colors don't match a valid Rubik's cube configuration\n"
                    "• Some facelets have incorrect or inconsistent colors\n"
                    "• The cube configuration violates physical constraints\n\n"
                    "RECOMMENDED: Use 'Load from Scramble' button instead.\n"
                    "This guarantees a valid, solvable cube state."
                )
                self.status_label.config(text="Error: Cannot resolve cube state")
                return
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error converting cube state: {e}\n\n"
                "Please try using 'Load from Scramble' to input a valid cube state."
            )
            return
        
        if not state.is_valid():
            messagebox.showerror(
                "Error",
                "Invalid cube state! The cube configuration violates physical constraints."
            )
            return
        
        if state.is_solved():
            messagebox.showinfo("Info", "Cube is already solved!")
            self.solution = []
            self.solution_text.delete(1.0, tk.END)
            self.solution_text.insert(1.0, "Cube is already solved!")
            return
        
        # Solve in background thread
        self.solving = True
        self.status_label.config(text="Solving... Please wait...")
        self.root.update()
        
        def solve_thread():
            try:
                # Initialize heuristic if needed
                if self.heuristic is None:
                    self.status_label.config(text="Building pattern databases...")
                    self.root.update()
                    self.heuristic = Heuristic()
                
                if self.solver is None:
                    self.solver = IDAStar(self.heuristic)
                
                # Solve
                self.status_label.config(text="Searching for solution...")
                self.root.update()
                solution = self.solver.solve(state, max_iterations=50)
                
                if solution:
                    self.solution = solution
                    solution_str = " ".join(solution)
                    self.solution_text.delete(1.0, tk.END)
                    self.solution_text.insert(1.0, f"Solution ({len(solution)} moves): {solution_str}")
                    self.status_label.config(text=f"Solution found! {len(solution)} moves")
                else:
                    self.solution = None
                    self.solution_text.delete(1.0, tk.END)
                    self.solution_text.insert(1.0, "No solution found within limits.")
                    self.status_label.config(text="No solution found")
                    messagebox.showwarning("Warning", "No solution found within iteration limit.")
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
        
        self.status_label.config(text="Animating solution...")
        
        # Convert current state to cubie model
        try:
            current_state = self.visualizer.to_cube_state()
            if current_state is None:
                messagebox.showerror(
                    "Error",
                    "Could not resolve cube state for animation.\n"
                    "Please ensure the cube state is valid."
                )
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error converting cube state: {e}")
            return
        
        # Animate each move
        for i, move_name in enumerate(self.solution):
            if move_name in MOVE_TABLE:
                current_state = MOVE_TABLE[move_name].apply(current_state)
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

