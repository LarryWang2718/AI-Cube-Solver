"""
Pattern Database (PDB) construction and heuristics.

Implements:
- Corner Orientation PDB (3^7 = 2187 states)
- Edge Orientation PDB (2^11 = 2048 states)
- Corner Permutation PDB (8! = 40320 states)
"""

import numpy as np
from collections import deque
from cube_state import CubeState, solved_state
from moves import ALL_MOVES, MOVE_TABLE


class PatternDatabase:
    """Base class for pattern databases."""
    
    def __init__(self, size: int):
        self.size = size
        self.pdb = np.full(size, np.inf, dtype=np.float32)
    
    def get(self, index: int) -> float:
        """Get heuristic value for a given abstract state index."""
        if 0 <= index < self.size:
            return self.pdb[index]
        return np.inf
    
    def build(self):
        """Build the pattern database. Override in subclasses."""
        raise NotImplementedError


class CornerOrientationPDB(PatternDatabase):
    """
    Corner Orientation Pattern Database.
    
    Abstracts state to (o_c(0), ..., o_c(6)) ∈ {0,1,2}^7
    o_c(7) is determined by the constraint: sum ≡ 0 (mod 3)
    """
    
    def __init__(self):
        super().__init__(3**7)  # 2187 states
    
    def abstract(self, state: CubeState) -> int:
        """
        Extract corner orientation pattern and return index.
        
        index = sum_{i=0}^{6} o_c(i) * 3^i
        """
        index = 0
        for i in range(7):
            index += int(state.corner_orient[i]) * (3 ** i)
        return index
    
    def build(self):
        """Build PDB using reverse BFS from solved state."""
        print("Building Corner Orientation PDB...")
        
        # Initialize: solved state has index 0 and distance 0
        self.pdb[0] = 0
        
        # BFS queue: (state, distance)
        queue = deque([(solved_state(), 0)])
        visited = set()
        visited.add(0)
        
        depth = 0
        nodes_at_depth = 1
        
        while queue:
            state, dist = queue.popleft()
            nodes_at_depth -= 1
            
            # Apply all moves
            for move in ALL_MOVES:
                next_state = move.apply(state)
                abstract_index = self.abstract(next_state)
                
                # If we haven't seen this abstract state, add it
                if abstract_index not in visited:
                    visited.add(abstract_index)
                    self.pdb[abstract_index] = dist + 1
                    queue.append((next_state, dist + 1))
            
            if nodes_at_depth == 0:
                depth += 1
                nodes_at_depth = len(queue)
                if depth % 2 == 0:
                    print(f"  Depth {depth}: {len(visited)}/{self.size} states explored")
        
        print(f"Corner Orientation PDB built: {len(visited)}/{self.size} states")
        print(f"  Max depth: {depth}")
        print(f"  Coverage: {100 * len(visited) / self.size:.1f}%")


class EdgeOrientationPDB(PatternDatabase):
    """
    Edge Orientation Pattern Database.
    
    Abstracts state to (o_e(0), ..., o_e(10)) ∈ {0,1}^11
    o_e(11) is determined by the constraint: sum ≡ 0 (mod 2)
    """
    
    def __init__(self):
        super().__init__(2**11)  # 2048 states
    
    def abstract(self, state: CubeState) -> int:
        """
        Extract edge orientation pattern and return index.
        
        index = sum_{i=0}^{10} o_e(i) * 2^i
        """
        index = 0
        for i in range(11):
            index += int(state.edge_orient[i]) * (2 ** i)
        return index
    
    def build(self):
        """Build PDB using reverse BFS from solved state."""
        print("Building Edge Orientation PDB...")
        
        # Initialize: solved state has index 0 and distance 0
        self.pdb[0] = 0
        
        # BFS queue: (state, distance)
        queue = deque([(solved_state(), 0)])
        visited = set()
        visited.add(0)
        
        depth = 0
        nodes_at_depth = 1
        
        while queue:
            state, dist = queue.popleft()
            nodes_at_depth -= 1
            
            # Apply all moves
            for move in ALL_MOVES:
                next_state = move.apply(state)
                abstract_index = self.abstract(next_state)
                
                # If we haven't seen this abstract state, add it
                if abstract_index not in visited:
                    visited.add(abstract_index)
                    self.pdb[abstract_index] = dist + 1
                    queue.append((next_state, dist + 1))
            
            if nodes_at_depth == 0:
                depth += 1
                nodes_at_depth = len(queue)
                if depth % 2 == 0:
                    print(f"  Depth {depth}: {len(visited)}/{self.size} states explored")
        
        print(f"Edge Orientation PDB built: {len(visited)}/{self.size} states")
        print(f"  Max depth: {depth}")
        print(f"  Coverage: {100 * len(visited) / self.size:.1f}%")


class CornerPermutationPDB(PatternDatabase):
    """
    Corner Permutation Pattern Database.
    
    Abstracts state to corner permutation p_c ∈ S_8
    Encoded using factorial number system (Lehmer code)
    """
    
    def __init__(self):
        super().__init__(40320)  # 8! = 40320 states
    
    def abstract(self, state: CubeState) -> int:
        """
        Extract corner permutation and return index using Lehmer code.
        
        The Lehmer code encodes a permutation as a sequence of numbers
        representing how many elements to the right are smaller.
        """
        perm = state.corner_perm.copy()
        index = 0
        factorial = 1
        
        for i in range(7, 0, -1):
            # Count elements to the right that are smaller
            count = 0
            for j in range(i + 1, 8):
                if perm[j] < perm[i]:
                    count += 1
            index += count * factorial
            factorial *= (8 - i)
        
        return index
    
    def build(self):
        """Build PDB using reverse BFS from solved state."""
        print("Building Corner Permutation PDB...")
        
        # Initialize: solved state has index 0 and distance 0
        self.pdb[0] = 0
        
        # BFS queue: (state, distance)
        queue = deque([(solved_state(), 0)])
        visited = set()
        visited.add(0)
        
        depth = 0
        nodes_at_depth = 1
        
        while queue:
            state, dist = queue.popleft()
            nodes_at_depth -= 1
            
            # Apply all moves
            for move in ALL_MOVES:
                next_state = move.apply(state)
                abstract_index = self.abstract(next_state)
                
                # If we haven't seen this abstract state, add it
                if abstract_index not in visited:
                    visited.add(abstract_index)
                    self.pdb[abstract_index] = dist + 1
                    queue.append((next_state, dist + 1))
            
            if nodes_at_depth == 0:
                depth += 1
                nodes_at_depth = len(queue)
                if depth % 3 == 0:
                    print(f"  Depth {depth}: {len(visited)}/{self.size} states explored")
        
        print(f"Corner Permutation PDB built: {len(visited)}/{self.size} states")
        print(f"  Max depth: {depth}")
        print(f"  Coverage: {100 * len(visited) / self.size:.1f}%")


def build_all_pdbs():
    """Build all pattern databases."""
    co_pdb = CornerOrientationPDB()
    co_pdb.build()
    
    eo_pdb = EdgeOrientationPDB()
    eo_pdb.build()
    
    cp_pdb = CornerPermutationPDB()
    cp_pdb.build()
    
    return co_pdb, eo_pdb, cp_pdb

