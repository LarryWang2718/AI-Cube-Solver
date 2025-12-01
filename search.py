"""
Search algorithm: IDA*
"""

from cube_state import CubeState
from moves import ALL_MOVES, MOVE_INVERSES, MOVE_INVERSE_TABLE, MOVE_TO_FACE, FACE_TO_MOVES
from heuristics import Heuristic


FAIL = object()


class IDAStar:
    """IDA* algorithm with pattern database heuristics."""
    
    def __init__(self, heuristic: Heuristic = None):
        """
        Initialize IDA* solver.
        
        Args:
            heuristic: Heuristic object (will be created if None)
        """
        if heuristic is None:
            self.heuristic = Heuristic()
        else:
            self.heuristic = heuristic
        
        self.nodes_expanded = 0
        self.max_depth_reached = 0
    
    def solve(self, initial_state: CubeState, max_iterations: int = 50, verbose: bool = True):
        """
        Solve using IDA*.
        
        Args:
            initial_state: starting cube state
            max_iterations: maximum number of iterations (default 50)
            verbose: whether to print progress messages (default True)
        
        Returns:
            List of move names representing the solution, or None if not found
        """
        self.nodes_expanded = 0
        self.max_depth_reached = 0
        
        # Initial threshold
        h0 = self.heuristic.h(initial_state)
        threshold = h0
        
        # Allocate path buffer once (Fix #4)
        max_depth = 50  # Reasonable upper bound
        path = [None] * max_depth
        
        if verbose:
            print(f"Initial heuristic value: {h0:.1f}")
            print(f"Starting IDA* search...")
        
        for iteration in range(max_iterations):
            if verbose:
                print(f"Iteration {iteration + 1}: threshold = {threshold:.1f}")
            
            # Create a working copy of the state for this iteration
            working_state = initial_state.copy()
            
            # Clear path buffer for this iteration (important for correctness)
            # Path is reused across iterations, so we need to ensure old values don't interfere
            # Since we start with path_len=0, we don't need to clear, but let's be safe
            # Actually, we don't need to clear since path_len=0 means we only read path[0:path_len]
            
            result, next_threshold = self._search(working_state, 0, threshold, None, path, 0)
            
            if isinstance(result, list):
                if verbose:
                    print(f"Solution found! Expanded {self.nodes_expanded} nodes")
                return result
            
            if next_threshold == float('inf'):
                if verbose:
                    print("No solution found within threshold")
                return None
            
            threshold = next_threshold
        
        if verbose:
            print(f"Reached maximum iterations ({max_iterations})")
        return None
    
    def _search(self, state: CubeState, g: float, threshold: float,
               last_move_name: str, path: list, path_len: int):
        """
        Recursive IDA* search.
        
        Returns:
            (result, next_threshold) where:
            - result is either a solution path (list) or FAIL
            - next_threshold is the minimum f-value that exceeded threshold
        """
        self.nodes_expanded += 1
        self.max_depth_reached = max(self.max_depth_reached, path_len)
        
        h = self.heuristic.h(state)
        f = g + h
        
        # Bound check
        if f > threshold:
            return FAIL, f
        
        # Goal check
        if state.is_solved():
            # Return path up to current depth (Fix #4)
            return path[:path_len], threshold
        
        min_overflow = float('inf')
        
        # Get face of last move for face-axis pruning
        last_face = None
        if last_move_name:
            last_face = MOVE_TO_FACE.get(last_move_name)
        
        for move in ALL_MOVES:
            # Prune immediate inverse
            if last_move_name and move.name == MOVE_INVERSES.get(last_move_name):
                continue
            
            # Face-axis pruning: skip moves on the same face as last move
            if last_face:
                move_face = MOVE_TO_FACE.get(move.name)
                if move_face == last_face:
                    continue
            
            # Apply move in-place (Fix #2)
            move.apply_in_place(state)
            path[path_len] = move.name  # Fix #4 - no list concatenation
            
            result, next_threshold = self._search(
                state, g + 1, threshold, move.name, path, path_len + 1
            )
            
            # Undo move (Fix #2)
            inverse_move = MOVE_INVERSE_TABLE[move]
            inverse_move.apply_in_place(state)
            
            if isinstance(result, list):
                return result, threshold
            
            # Track minimum f-value that exceeded threshold
            if next_threshold < min_overflow:
                min_overflow = next_threshold
        
        return FAIL, min_overflow

