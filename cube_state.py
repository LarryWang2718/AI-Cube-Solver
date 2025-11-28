"""
Cube State Representation using the Cubie Model.

A cube state is represented as (p_c, o_c, p_e, o_e) where:
- p_c: permutation of corner cubies (8 corners)
- o_c: corner orientations (0, 1, or 2)
- p_e: permutation of edge cubies (12 edges)
- o_e: edge orientations (0 or 1)
"""

import numpy as np
from typing import Tuple


class CubeState:
    """Represents a 3x3x3 Rubik's Cube state using the cubie model."""
    
    # Corner positions: 8 corners indexed 0-7
    # Edge positions: 12 edges indexed 0-11
    
    def __init__(self, 
                 corner_perm: np.ndarray = None,
                 corner_orient: np.ndarray = None,
                 edge_perm: np.ndarray = None,
                 edge_orient: np.ndarray = None):
        """
        Initialize cube state.
        
        Args:
            corner_perm: array of 8 integers, corner_perm[i] = j means corner cubie j is at position i
            corner_orient: array of 8 integers in {0,1,2}, orientation of corner at position i
            edge_perm: array of 12 integers, edge_perm[i] = j means edge cubie j is at position i
            edge_orient: array of 12 integers in {0,1}, orientation of edge at position i
        """
        if corner_perm is None:
            # Solved state
            self.corner_perm = np.arange(8, dtype=np.int32)
            self.corner_orient = np.zeros(8, dtype=np.int32)
            self.edge_perm = np.arange(12, dtype=np.int32)
            self.edge_orient = np.zeros(12, dtype=np.int32)
        else:
            self.corner_perm = np.array(corner_perm, dtype=np.int32)
            self.corner_orient = np.array(corner_orient, dtype=np.int32)
            self.edge_perm = np.array(edge_perm, dtype=np.int32)
            self.edge_orient = np.array(edge_orient, dtype=np.int32)
    
    def copy(self):
        """Create a deep copy of this state."""
        return CubeState(
            self.corner_perm.copy(),
            self.corner_orient.copy(),
            self.edge_perm.copy(),
            self.edge_orient.copy()
        )
    
    def is_solved(self) -> bool:
        """Check if the cube is in the solved state."""
        return (np.array_equal(self.corner_perm, np.arange(8)) and
                np.all(self.corner_orient == 0) and
                np.array_equal(self.edge_perm, np.arange(12)) and
                np.all(self.edge_orient == 0))
    
    def is_valid(self) -> bool:
        """
        Check if the state satisfies physical constraints:
        - Sign of corner permutation = sign of edge permutation
        - Sum of corner orientations ≡ 0 (mod 3)
        - Sum of edge orientations ≡ 0 (mod 2)
        """
        # Check permutation parity
        corner_parity = self._permutation_parity(self.corner_perm)
        edge_parity = self._permutation_parity(self.edge_perm)
        if corner_parity != edge_parity:
            return False
        
        # Check corner orientation sum
        if np.sum(self.corner_orient) % 3 != 0:
            return False
        
        # Check edge orientation sum
        if np.sum(self.edge_orient) % 2 != 0:
            return False
        
        return True
    
    @staticmethod
    def _permutation_parity(perm: np.ndarray) -> int:
        """Compute the parity (sign) of a permutation. Returns 0 for even, 1 for odd."""
        n = len(perm)
        visited = np.zeros(n, dtype=bool)
        parity = 0
        
        for i in range(n):
            if not visited[i]:
                cycle_length = 0
                j = i
                while not visited[j]:
                    visited[j] = True
                    j = perm[j]
                    cycle_length += 1
                if cycle_length > 1:
                    parity = (parity + cycle_length - 1) % 2
        
        return parity
    
    def __eq__(self, other):
        """Check equality of two cube states."""
        if not isinstance(other, CubeState):
            return False
        return (np.array_equal(self.corner_perm, other.corner_perm) and
                np.array_equal(self.corner_orient, other.corner_orient) and
                np.array_equal(self.edge_perm, other.edge_perm) and
                np.array_equal(self.edge_orient, other.edge_orient))
    
    def __hash__(self):
        """Hash function for use in sets/dicts."""
        return hash((
            tuple(self.corner_perm),
            tuple(self.corner_orient),
            tuple(self.edge_perm),
            tuple(self.edge_orient)
        ))


def solved_state() -> CubeState:
    """Return the solved cube state."""
    return CubeState()

