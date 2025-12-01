"""
Cube State Representation using the Cubie Model.

A cube state is represented as (p_c, o_c, p_e, o_e) where:
- p_c: permutation of corner cubies (8 corners)
- o_c: corner orientations (0, 1, or 2)
- p_e: permutation of edge cubies (12 edges)
- o_e: edge orientations (0 or 1)
"""


class CubeState:
    """Represents a 3x3x3 Rubik's Cube state using the cubie model."""
    
    # Corner positions: 8 corners indexed 0-7
    # Edge positions: 12 edges indexed 0-11
    
    def __init__(self, 
                 corner_perm: list = None,
                 corner_orient: list = None,
                 edge_perm: list = None,
                 edge_orient: list = None):
        """
        Initialize cube state.
        
        Args:
            corner_perm: list of 8 integers, corner_perm[i] = j means corner cubie j is at position i
            corner_orient: list of 8 integers in {0,1,2}, orientation of corner at position i
            edge_perm: list of 12 integers, edge_perm[i] = j means edge cubie j is at position i
            edge_orient: list of 12 integers in {0,1}, orientation of edge at position i
        """
        if corner_perm is None:
            # Solved state
            self.corner_perm = list(range(8))
            self.corner_orient = [0] * 8
            self.edge_perm = list(range(12))
            self.edge_orient = [0] * 12
        else:
            self.corner_perm = list(corner_perm)
            self.corner_orient = list(corner_orient)
            self.edge_perm = list(edge_perm)
            self.edge_orient = list(edge_orient)
    
    def copy(self):
        """Create a copy of this state. Optimized for performance."""
        s = CubeState.__new__(CubeState)
        s.corner_perm = self.corner_perm[:]   # list slice copy only
        s.corner_orient = self.corner_orient[:]
        s.edge_perm = self.edge_perm[:]
        s.edge_orient = self.edge_orient[:]
        return s
    
    def is_solved(self) -> bool:
        """Check if the cube is in the solved state."""
        return (self.corner_perm == list(range(8)) and
                all(x == 0 for x in self.corner_orient) and
                self.edge_perm == list(range(12)) and
                all(x == 0 for x in self.edge_orient))
    
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
        if sum(self.corner_orient) % 3 != 0:
            return False
        
        # Check edge orientation sum
        if sum(self.edge_orient) % 2 != 0:
            return False
        
        return True
    
    @staticmethod
    def _permutation_parity(perm: list) -> int:
        """Compute the parity (sign) of a permutation. Returns 0 for even, 1 for odd."""
        n = len(perm)
        visited = [False] * n
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
        return (self.corner_perm == other.corner_perm and
                self.corner_orient == other.corner_orient and
                self.edge_perm == other.edge_perm and
                self.edge_orient == other.edge_orient)
    
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

