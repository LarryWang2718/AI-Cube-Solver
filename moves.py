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
    """
    Create move tables for all 18 moves.
    
    Corner positions (0-7):
    0: URF, 1: UFL, 2: ULB, 3: UBR, 4: DFR, 5: DLF, 6: DBL, 7: DRB
    
    Edge positions (0-11) - Paper order: uf, ur, ub, ul, lf, fr, rb, bl, df, dr, db, dl
    0: UF, 1: UR, 2: UB, 3: UL, 4: FL, 5: FR, 6: BR, 7: BL, 8: DF, 9: DR, 10: DB, 11: DL
    """
    moves = {}
    
    # U move (clockwise)
    # Corners: 0->1->2->3->0, orientations unchanged (stay on U face)
    # Edges: UF->UR->UB->UL->UF (paper order: 0->1->2->3->0)
    # All top edges stay on U face, so reference stays on U - orientations unchanged
    moves['U'] = Move('U',
        corner_perm=[1, 2, 3, 0, 4, 5, 6, 7],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11],
        edge_orient_delta=[0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    # U2 move
    moves['U2'] = Move('U2',
        corner_perm=[2, 3, 0, 1, 4, 5, 6, 7],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[2, 3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    # U' move (counterclockwise)
    moves["U'"] = Move("U'",
        corner_perm=[3, 0, 1, 2, 4, 5, 6, 7],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    # D move (clockwise, viewed from top)
    # Corners: 4->5->6->7->4
    # Edges: DF->DR->DB->DL->DF (paper order: 8->9->10->11->8)
    moves['D'] = Move('D',
        corner_perm=[0, 1, 2, 3, 7, 4, 5, 6],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 8],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves['D2'] = Move('D2',
        corner_perm=[0, 1, 2, 3, 6, 7, 4, 5],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 8, 9],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves["D'"] = Move("D'",
        corner_perm=[0, 1, 2, 3, 5, 6, 7, 4],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 1, 2, 3, 4, 5, 6, 7, 11, 8, 9, 10],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    # L move (clockwise, viewed from left)
    # Corners: 1->5->6->2->1, with orientation changes
    # Edges: UL->FL->DL->BL->UL (paper order: 3->4->11->7->3)
    # L moves don't flip edges (edges stay on same face orientation relative to L)
    moves['L'] = Move('L',
        corner_perm=[0, 2, 6, 3, 4, 1, 5, 7],
        corner_orient_delta=[0, 2, 1, 0, 0, 1, 2, 0],  # L moves twist corners
        edge_perm=[0, 1, 2, 4, 11, 5, 6, 3, 8, 9, 10, 7],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves['L2'] = Move('L2',
        corner_perm=[0, 6, 5, 3, 4, 2, 1, 7],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 1, 2, 11, 7, 5, 6, 4, 8, 9, 10, 3],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves["L'"] = Move("L'",
        corner_perm=[0, 2, 6, 3, 4, 1, 5, 7],
        corner_orient_delta=[0, 2, 1, 0, 0, 2, 1, 0],
        edge_perm=[0, 1, 2, 7, 3, 5, 6, 11, 8, 9, 10, 4],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    # R move (clockwise, viewed from right)
    # Corners: 0->4->7->3->0, with orientation changes
    # Edges: UR->FR->DR->BR->UR (paper order: 1->5->9->6->1)
    # R moves don't flip edges (edges stay on same face orientation relative to R)
    moves['R'] = Move('R',
        corner_perm=[4, 1, 2, 0, 7, 5, 6, 3],
        corner_orient_delta=[1, 0, 0, 2, 2, 0, 0, 1],
        edge_perm=[0, 5, 2, 3, 4, 9, 1, 7, 8, 6, 10, 11],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves['R2'] = Move('R2',
        corner_perm=[7, 1, 2, 4, 3, 5, 6, 0],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 9, 2, 3, 4, 6, 5, 7, 8, 1, 10, 11],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves["R'"] = Move("R'",
        corner_perm=[3, 1, 2, 7, 0, 5, 6, 4],
        corner_orient_delta=[2, 0, 0, 1, 1, 0, 0, 2],
        edge_perm=[0, 6, 2, 3, 4, 1, 9, 7, 8, 5, 10, 11],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    # F move (clockwise, viewed from front)
    # Corners: 0->1->5->4->0, with orientation changes
    # Edges: UF->FL->DF->FR->UF (paper order: 0->4->8->5->0), with orientation changes
    moves['F'] = Move('F',
        corner_perm=[1, 5, 2, 3, 0, 4, 6, 7],
        corner_orient_delta=[1, 2, 0, 0, 2, 1, 0, 0],
        edge_perm=[4, 1, 2, 3, 0, 8, 6, 7, 5, 9, 10, 11],
        edge_orient_delta=[1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0]
    )
    
    moves['F2'] = Move('F2',
        corner_perm=[5, 4, 2, 3, 1, 0, 6, 7],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[5, 1, 2, 3, 8, 4, 6, 7, 0, 9, 10, 11],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves["F'"] = Move("F'",
        corner_perm=[4, 0, 2, 3, 5, 1, 6, 7],
        corner_orient_delta=[2, 1, 0, 0, 1, 2, 0, 0],
        edge_perm=[5, 1, 2, 3, 8, 0, 6, 7, 4, 9, 10, 11],
        edge_orient_delta=[1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0]
    )
    
    # B move (clockwise, viewed from back)
    # Corners: 2->3->7->6->2, with orientation changes
    # Edges: UB->BR->DB->BL->UB (paper order: 2->6->10->7->2), with orientation changes
    moves['B'] = Move('B',
        corner_perm=[0, 1, 3, 7, 4, 5, 2, 6],
        corner_orient_delta=[0, 0, 1, 2, 0, 0, 2, 1],
        edge_perm=[0, 1, 6, 3, 4, 5, 2, 10, 8, 9, 7, 11],
        edge_orient_delta=[0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0]
    )
    
    moves['B2'] = Move('B2',
        corner_perm=[0, 1, 7, 6, 4, 5, 3, 2],
        corner_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0],
        edge_perm=[0, 1, 7, 3, 4, 5, 10, 6, 8, 9, 2, 11],
        edge_orient_delta=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    
    moves["B'"] = Move("B'",
        corner_perm=[0, 1, 6, 2, 4, 5, 7, 3],
        corner_orient_delta=[0, 0, 2, 1, 0, 0, 1, 2],
        edge_perm=[0, 1, 7, 3, 4, 5, 10, 2, 8, 9, 6, 11],
        edge_orient_delta=[0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0]
    )
    
    return moves


# Create move tables
MOVE_TABLE = create_move_tables()

# List of all moves
ALL_MOVES = [MOVE_TABLE[name] for name in MOVE_NAMES]

