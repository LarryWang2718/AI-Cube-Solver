"""
Search algorithms: IDDFS and IDA*
"""

from cube_state import CubeState
from moves import ALL_MOVES, MOVE_INVERSES
from heuristics import Heuristic


FOUND = object()
FAIL = object()


class IDDFS:
    """Iterative Deepening Depth-First Search (baseline)."""
    
    def __init__(self):
        self.nodes_expanded = 0
    
    def solve(self, initial_state: CubeState, max_depth: int = 20):
        """
        Solve using IDDFS.
        
        Args:
            initial_state: starting cube state
            max_depth: maximum depth to search (default 20)
        
        Returns:
            List of move names representing the solution, or None if not found
        """
        self.nodes_expanded = 0
        
        for depth in range(max_depth + 1):
            result = self._dfs_limited(initial_state, depth, None, [])
            if result is FOUND:
                return result
            elif isinstance(result, list):
                return result
        
        return None
    
    def _dfs_limited(self, state: CubeState, depth: int, 
                    last_move_name: str, path: list):
        """Depth-limited DFS."""
        self.nodes_expanded += 1
        
        if state.is_solved():
            return path
        
        if depth == 0:
            return FAIL
        
        for move in ALL_MOVES:
            # Prune immediate inverse
            if last_move_name and move.name == MOVE_INVERSES.get(last_move_name):
                continue
            
            next_state = move.apply(state)
            result = self._dfs_limited(next_state, depth - 1, move.name, 
                                      path + [move.name])
            
            if result is not FAIL:
                return result
        
        return FAIL


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
    
    def solve(self, initial_state: CubeState, max_iterations: int = 50):
        """
        Solve using IDA*.
        
        Args:
            initial_state: starting cube state
            max_iterations: maximum number of iterations (default 50)
        
        Returns:
            List of move names representing the solution, or None if not found
        """
        self.nodes_expanded = 0
        self.max_depth_reached = 0
        
        # Initial threshold
        h0 = self.heuristic.h(initial_state)
        threshold = h0
        
        print(f"Initial heuristic value: {h0:.1f}")
        print(f"Starting IDA* search...")
        
        for iteration in range(max_iterations):
            print(f"Iteration {iteration + 1}: threshold = {threshold:.1f}")
            
            result, next_threshold = self._search(initial_state, 0, threshold, None, [])
            
            if isinstance(result, list):
                print(f"Solution found! Expanded {self.nodes_expanded} nodes")
                return result
            
            if next_threshold == float('inf'):
                print("No solution found within threshold")
                return None
            
            threshold = next_threshold
        
        print(f"Reached maximum iterations ({max_iterations})")
        return None
    
    def _search(self, state: CubeState, g: float, threshold: float,
               last_move_name: str, path: list):
        """
        Recursive IDA* search.
        
        Returns:
            (result, next_threshold) where:
            - result is either a solution path (list) or FOUND/FAIL
            - next_threshold is the minimum f-value that exceeded threshold
        """
        self.nodes_expanded += 1
        self.max_depth_reached = max(self.max_depth_reached, len(path))
        
        h = self.heuristic.h(state)
        f = g + h
        
        # Bound check
        if f > threshold:
            return FAIL, f
        
        # Goal check
        if state.is_solved():
            return path, threshold
        
        min_overflow = float('inf')
        
        for move in ALL_MOVES:
            # Prune immediate inverse
            if last_move_name and move.name == MOVE_INVERSES.get(last_move_name):
                continue
            
            next_state = move.apply(state)
            result, next_threshold = self._search(
                next_state, g + 1, threshold, move.name, path + [move.name]
            )
            
            if isinstance(result, list):
                return result, threshold
            
            # Track minimum f-value that exceeded threshold
            if next_threshold < min_overflow:
                min_overflow = next_threshold
        
        return FAIL, min_overflow

