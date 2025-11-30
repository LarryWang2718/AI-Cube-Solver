"""
Move definitions and application for the Rubik's Cube.

Each move is represented as (σ_c, δ_c, σ_e, δ_e) where:
- σ_c: permutation of corner positions
- δ_c: change in corner orientation
- σ_e: permutation of edge positions
- δ_e: change in edge orientation
"""

import numpy as np
from cube_state import CubeState


# Move names in quarter-turn metric
MOVE_NAMES = [
    'U', 'U2', "U'",
    'D', 'D2', "D'",
    'L', 'L2', "L'",
    'R', 'R2', "R'",
    'F', 'F2', "F'",
    'B', 'B2', "B'"
]

# Move inverses mapping
MOVE_INVERSES = {
    'U': "U'", "U'": 'U', 'U2': 'U2',
    'D': "D'", "D'": 'D', 'D2': 'D2',
    'L': "L'", "L'": 'L', 'L2': 'L2',
    'R': "R'", "R'": 'R', 'R2': 'R2',
    'F': "F'", "F'": 'F', 'F2': 'F2',
    'B': "B'", "B'": 'B', 'B2': 'B2',
}


class Move:
    """Represents a move on the cube."""
    
    def __init__(self, name: str,
                 corner_perm: np.ndarray,
                 corner_orient_delta: np.ndarray,
                 edge_perm: np.ndarray,
                 edge_orient_delta: np.ndarray):
        """
        Initialize a move.
        
        Args:
            name: move name (e.g., 'U', "U'", 'U2')
            corner_perm: permutation of corner positions (8 elements)
            corner_orient_delta: change in corner orientation (8 elements)
            edge_perm: permutation of edge positions (12 elements)
            edge_orient_delta: change in edge orientation (12 elements)
        """
        self.name = name
        self.corner_perm = np.array(corner_perm, dtype=np.int32)
        self.corner_orient_delta = np.array(corner_orient_delta, dtype=np.int32)
        self.edge_perm = np.array(edge_perm, dtype=np.int32)
        self.edge_orient_delta = np.array(edge_orient_delta, dtype=np.int32)
    
    def apply(self, state: CubeState) -> CubeState:
        """
        Apply this move to a state, returning a new state.
        
        The successor state s' = m(s) is computed as:
        - p_c'(i) = p_c(σ_c^{-1}(i))
        - o_c'(i) = (o_c(σ_c^{-1}(i)) + δ_c(i)) mod 3
        - p_e'(i) = p_e(σ_e^{-1}(i))
        - o_e'(i) = (o_e(σ_e^{-1}(i)) + δ_e(i)) mod 2
        """
        # Compute inverse permutations
        corner_perm_inv = np.argsort(self.corner_perm)
        edge_perm_inv = np.argsort(self.edge_perm)
        
        # Apply corner permutation and orientation
        new_corner_perm = state.corner_perm[corner_perm_inv]
        new_corner_orient = (state.corner_orient[corner_perm_inv] + 
                            self.corner_orient_delta) % 3
        
        # Apply edge permutation and orientation
        new_edge_perm = state.edge_perm[edge_perm_inv]
        new_edge_orient = (state.edge_orient[edge_perm_inv] + 
                          self.edge_orient_delta) % 2
        
        return CubeState(new_corner_perm, new_corner_orient,
                        new_edge_perm, new_edge_orient)
    
    def __repr__(self):
        return self.name


def create_move_tables():
    """Create move tables for all 18 moves."""
    moves = {}
    
    moves['U'] = Move('U',
        corner_perm=[0, 1, 4, 2, 5, 3, 6, 7],  # 2->4, 4->5, 5->3, 3->2
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11],  # 0->1, 1->2, 2->3, 3->0
        edge_orient_delta=[0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves['U2'] = Move('U2',
        corner_perm=[0, 1, 5, 4, 3, 2, 6, 7],  # 2->5, 5->2, 4->3, 3->4
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[2, 3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11],  # 0->2, 1->3, 2->0, 3->1
        edge_orient_delta=[1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves["U'"] = Move("U'",
        corner_perm=[0, 1, 3, 5, 2, 4, 6, 7],  # 2->3, 3->5, 5->4, 4->2
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11],  # 0->3, 1->0, 2->1, 3->2
        edge_orient_delta=[1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves['D'] = Move('D',
        corner_perm=[1, 7, 2, 3, 4, 5, 0, 6],  # 0->1, 1->7, 7->6, 6->0
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 8],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0]
    )
    
    moves['D2'] = Move('D2',
        corner_perm=[7, 6, 2, 3, 4, 5, 1, 0],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 8, 9],  # 8->10, 9->11, 10->8, 11->9
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
    )
    
    moves["D'"] = Move("D'",
        corner_perm=[6, 0, 2, 3, 4, 5, 7, 1],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 1, 2, 3, 4, 5, 6, 7, 11, 8, 9, 10],  # 8->11, 9->8, 10->9, 11->10
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]
    )
    
    moves['L'] = Move('L',
        corner_perm=[0, 1, 2, 3, 6, 4, 7, 5],  # 4->6, 6->7, 7->5, 5->4
        corner_orient_delta=[0, 0, 0, 0, 2, 1, 1, 2],  # 4: U->D +2, 5: U->U +1, 6: D->D +2, 7: D->U +1
        edge_perm=[0, 1, 2, 4, 11, 5, 6, 3, 8, 9, 10, 7],  # 3->4, 4->11, 11->7, 7->3
        edge_orient_delta=[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1]
    )
    
    moves['L2'] = Move('L2',
        corner_perm=[0, 1, 2, 3, 7, 6, 5, 4],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 1, 2, 11, 7, 5, 6, 4, 8, 9, 10, 3],  # 3->11, 4->7, 11->4, 7->3
        edge_orient_delta=[0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1]
    )
    
    moves["L'"] = Move("L'",
        corner_perm=[0, 1, 2, 3, 5, 7, 4, 6],
        corner_orient_delta=[0, 0, 0, 0, 2, 1, 1, 2],
        edge_perm=[0, 1, 2, 7, 3, 5, 6, 11, 8, 9, 10, 4],  # 3->7, 4->3, 11->11, 7->4
        edge_orient_delta=[0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]
    )
    
    moves["R'"] = Move("R'",
        corner_perm=[1, 3, 0, 2, 4, 5, 6, 7],
        corner_orient_delta=[2, 1, 1, 2, 0, 0, 0, 0],
        edge_perm=[0, 5, 2, 3, 4, 9, 1, 7, 8, 6, 10, 11],  # 1->6, 5->1, 9->5, 6->9
        edge_orient_delta=[0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
    )
    
    moves['R2'] = Move('R2',
        corner_perm=[3, 2, 1, 0, 4, 5, 6, 7],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 9, 2, 3, 4, 6, 5, 7, 8, 1, 10, 11],  # 1->9, 5->6, 9->1, 6->5
        edge_orient_delta=[0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0]
    )

    moves['R'] = Move('R',
        corner_perm=[2, 0, 3, 1, 4, 5, 6, 7],
        corner_orient_delta=[2, 1, 1, 2, 0, 0, 0, 0],
        edge_perm=[0, 6, 2, 3, 4, 1, 9, 7, 8, 5, 10, 11],  # 1->5, 5->9, 9->6, 6->1
        edge_orient_delta=[0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]
    )
    
    moves['F'] = Move('F',
        corner_perm=[6, 1, 0, 3, 2, 5, 4, 7],  # 2->0, 0->6, 6->4, 4->2
        corner_orient_delta=[1, 0, 2, 0, 1, 0, 2, 0],
        edge_perm=[5, 1, 2, 3, 0, 8, 6, 7, 4, 9, 10, 11],
        edge_orient_delta=[0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]
    )
    
    moves['F2'] = Move('F2',
        corner_perm=[4, 1, 6, 3, 0, 5, 2, 7],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[8, 1, 2, 3, 5, 4, 6, 7, 0, 9, 10, 11],
        edge_orient_delta=[1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0]
    )
    
    moves["F'"] = Move("F'",
        corner_perm=[2, 1, 4, 3, 6, 5, 0, 7],
        corner_orient_delta=[1, 0, 2, 0, 1, 0, 2, 0],
        edge_perm=[4, 1, 2, 3, 8, 0, 6, 7, 5, 9, 10, 11],
        edge_orient_delta=[1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    )
    
    moves["B'"] = Move("B'",
        corner_perm=[0, 7, 2, 1, 4, 3, 6, 5],
        corner_orient_delta=[0, 2, 0, 1, 0, 2, 0, 1],
        edge_perm=[0, 1, 6, 3, 4, 5, 10, 2, 8, 9, 7, 11],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]
    )
    
    moves['B2'] = Move('B2',
        corner_perm=[0, 5, 2, 7, 4, 1, 6, 3],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 1, 10, 3, 4, 5, 7, 6, 8, 9, 2, 11],
        edge_orient_delta=[0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0]
    )
    
    moves['B'] = Move('B',
        corner_perm=[0, 3, 2, 5, 4, 7, 6, 1],
        corner_orient_delta=[0, 2, 0, 1, 0, 2, 0, 1],
        edge_perm=[0, 1, 7, 3, 4, 5, 2, 10, 8, 9, 6, 11],
        edge_orient_delta=[0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0]
    )
    
    return moves


# Create move tables
MOVE_TABLE = create_move_tables()

# List of all moves
ALL_MOVES = [MOVE_TABLE[name] for name in MOVE_NAMES]

