"""
Conversion between visual cube representation (face colors) and cubie model.

This module handles the complex mapping between:
- Visual: 6 faces, each 3x3 grid of colors
- Cubie model: corner/edge permutations and orientations
"""

import numpy as np
from cube_state import CubeState
from moves import MOVE_TABLE


# Standard face colors
FACE_COLORS = ['W', 'Y', 'R', 'O', 'B', 'G']  # White, Yellow, Red, Orange, Blue, Green

# Face indices
U, L, F, R, B, D = 0, 1, 2, 3, 4, 5

# Corner cubie definition: (face1, pos1, face2, pos2, face3, pos3)
# Each corner is defined by 3 faces and their positions on those faces
CORNER_DEFINITIONS = [
    # Corner 0: URF (Up-Right-Front)
    ((U, 0, 2), (R, 0, 0), (F, 0, 2)),
    # Corner 1: UFL (Up-Front-Left)
    ((U, 0, 0), (F, 0, 0), (L, 0, 2)),
    # Corner 2: ULB (Up-Left-Back)
    ((U, 2, 0), (L, 0, 0), (B, 0, 2)),
    # Corner 3: UBR (Up-Back-Right)
    ((U, 2, 2), (B, 0, 0), (R, 0, 2)),
    # Corner 4: DFR (Down-Front-Right)
    ((D, 0, 2), (F, 2, 2), (R, 2, 0)),
    # Corner 5: DLF (Down-Left-Front)
    ((D, 0, 0), (L, 2, 2), (F, 2, 0)),
    # Corner 6: DBL (Down-Back-Left)
    ((D, 2, 0), (B, 2, 2), (L, 2, 0)),
    # Corner 7: DRB (Down-Right-Back)
    ((D, 2, 2), (R, 2, 2), (B, 2, 0)),
]

# Edge cubie definition: (face1, pos1, face2, pos2)
# Paper order: uf, ur, ub, ul, lf, fr, rb, bl, df, dr, db, dl
EDGE_DEFINITIONS = [
    # Edge 0: UF (Up-Front) - paper index 1
    ((U, 1, 2), (F, 0, 1)),
    # Edge 1: UR (Up-Right) - paper index 2
    ((U, 0, 1), (R, 0, 1)),
    # Edge 2: UB (Up-Back) - paper index 3
    ((U, 2, 1), (B, 0, 1)),
    # Edge 3: UL (Up-Left) - paper index 4
    ((U, 1, 0), (L, 0, 1)),
    # Edge 4: FL (Front-Left, paper calls it "lf") - paper index 5
    ((F, 1, 0), (L, 1, 2)),
    # Edge 5: FR (Front-Right) - paper index 6
    ((F, 1, 2), (R, 1, 0)),
    # Edge 6: BR (Back-Right, paper calls it "rb") - paper index 7
    ((B, 1, 0), (R, 1, 2)),
    # Edge 7: BL (Back-Left) - paper index 8
    ((B, 1, 2), (L, 1, 0)),
    # Edge 8: DF (Down-Front) - paper index 9
    ((D, 1, 2), (F, 2, 1)),
    # Edge 9: DR (Down-Right) - paper index 10
    ((D, 0, 1), (R, 2, 1)),
    # Edge 10: DB (Down-Back) - paper index 11
    ((D, 2, 1), (B, 2, 1)),
    # Edge 11: DL (Down-Left) - paper index 12
    ((D, 1, 0), (L, 2, 1)),
]

# Solved state: each cubie has specific colors
# Corner colors in solved state (order matches CORNER_DEFINITIONS: face order in definition)
# Standard: White=U, Yellow=D, Green=F, Blue=B, Orange=L, Red=R
SOLVED_CORNER_COLORS = [
    ['W', 'R', 'G'],  # URF: White-Up, Red-Right, Green-Front
    ['W', 'G', 'O'],  # UFL: White-Up, Green-Front, Orange-Left
    ['W', 'O', 'B'],  # ULB: White-Up, Orange-Left, Blue-Back
    ['W', 'B', 'R'],  # UBR: White-Up, Blue-Back, Red-Right
    ['Y', 'G', 'R'],  # DFR: Yellow-Down, Green-Front, Red-Right
    ['Y', 'O', 'G'],  # DLF: Yellow-Down, Orange-Left, Green-Front
    ['Y', 'B', 'O'],  # DBL: Yellow-Down, Blue-Back, Orange-Left
    ['Y', 'R', 'B'],  # DRB: Yellow-Down, Red-Right, Blue-Back
]

# Corner orientation definition based on paper's '+' markers
# Each corner cubie has a reference facet (marked with +) that should be on U or D face
# For top corners (0-3): reference facet is on U face (first facet, index 0)
# For bottom corners (4-7): reference facet is on D face (first facet, index 0)
# Orientation 0: reference facet is on U or D face (correct orientation)
# Orientation 1: reference facet rotated clockwise to a side face
# Orientation 2: reference facet rotated counterclockwise to a side face

# Reference facet color for each corner cubie (the color on the U/D face in solved state)
CORNER_REFERENCE_COLORS = [
    'W',  # Cubie 0 (URF): reference is White (on U)
    'W',  # Cubie 1 (UFL): reference is White (on U)
    'W',  # Cubie 2 (ULB): reference is White (on U)
    'W',  # Cubie 3 (UBR): reference is White (on U)
    'Y',  # Cubie 4 (DFR): reference is Yellow (on D)
    'Y',  # Cubie 5 (DLF): reference is Yellow (on D)
    'Y',  # Cubie 6 (DBL): reference is Yellow (on D)
    'Y',  # Cubie 7 (DRB): reference is Yellow (on D)
]

# For each corner position, which face index should have the reference facet (U or D)
CORNER_REFERENCE_FACES = [
    U,  # Position 0 (URF): reference should be on U
    U,  # Position 1 (UFL): reference should be on U
    U,  # Position 2 (ULB): reference should be on U
    U,  # Position 3 (UBR): reference should be on U
    D,  # Position 4 (DFR): reference should be on D
    D,  # Position 5 (DLF): reference should be on D
    D,  # Position 6 (DBL): reference should be on D
    D,  # Position 7 (DRB): reference should be on D
]

# Edge colors in solved state
# Paper order: uf, ur, ub, ul, lf, fr, rb, bl, df, dr, db, dl
# Order matches EDGE_DEFINITIONS: (face1_color, face2_color)
SOLVED_EDGE_COLORS = [
    ['W', 'G'],  # Edge 0 (UF): (U=W, F=G)
    ['W', 'R'],  # Edge 1 (UR): (U=W, R=R)
    ['W', 'B'],  # Edge 2 (UB): (U=W, B=B)
    ['W', 'O'],  # Edge 3 (UL): (U=W, L=O)
    ['G', 'O'],  # Edge 4 (FL): (F=G, L=O)
    ['G', 'R'],  # Edge 5 (FR): (F=G, R=R)
    ['B', 'R'],  # Edge 6 (BR): (B=B, R=R)
    ['B', 'O'],  # Edge 7 (BL): (B=B, L=O)
    ['Y', 'G'],  # Edge 8 (DF): (D=Y, F=G)
    ['Y', 'R'],  # Edge 9 (DR): (D=Y, R=R)
    ['Y', 'B'],  # Edge 10 (DB): (D=Y, B=B)
    ['Y', 'O'],  # Edge 11 (DL): (D=Y, L=O)
]

# Edge orientation definition based on paper's '+' markers
# Each edge cubie has a reference facet (marked with +) on a specific face
# According to paper: '+' on UR, UF, FR, DF, DR (on F/R/U faces)
#                     '+' on dl, db, lf, lu, bl, bu (on other faces)
# Orientation 0: reference facet is on the correct face (as defined below)
# Orientation 1: reference facet is flipped to the other face

# For each edge cubie, which face should have the reference facet (the one with +)
# Paper order: uf, ur, ub, ul, lf, fr, rb, bl, df, dr, db, dl
# Based on paper: '+' on UR, UF, FR, DF, DR (on F/R/U faces)
#                 '+' on dl, db, lf, lu, bl, bu (on other faces)
EDGE_REFERENCE_FACES = [
    U,  # Edge 0 (UF): reference on U face (uf)
    U,  # Edge 1 (UR): reference on U face (ur)
    B,  # Edge 2 (UB): reference on B face (bu)
    L,  # Edge 3 (UL): reference on L face (lu)
    L,  # Edge 4 (FL): reference on L face (lf)
    F,  # Edge 5 (FR): reference on F face (fr)
    R,  # Edge 6 (BR): reference on R face (rb)
    L,  # Edge 7 (BL): reference on L face (bl)
    F,  # Edge 8 (DF): reference on F face (df)
    R,  # Edge 9 (DR): reference on R face (dr)
    B,  # Edge 10 (DB): reference on B face (db)
    L,  # Edge 11 (DL): reference on L face (dl)
]

# For each edge position, which face should have the reference facet
# Paper order: uf, ur, ub, ul, lf, fr, rb, bl, df, dr, db, dl
# This is based on the position's definition and the paper's rules
EDGE_POSITION_REFERENCE_FACES = [
    U,  # Position 0 (UF): reference should be on U
    U,  # Position 1 (UR): reference should be on U
    B,  # Position 2 (UB): reference should be on B (bu)
    L,  # Position 3 (UL): reference should be on L (lu)
    L,  # Position 4 (FL): reference should be on L (lf)
    F,  # Position 5 (FR): reference should be on F
    R,  # Position 6 (BR): reference should be on R (rb)
    L,  # Position 7 (BL): reference should be on L (bl)
    F,  # Position 8 (DF): reference should be on F
    R,  # Position 9 (DR): reference should be on R
    B,  # Position 10 (DB): reference should be on B (db)
    L,  # Position 11 (DL): reference should be on L (dl)
]

# Reference color for each edge cubie (the color on the reference face in solved state)
# Paper order: uf, ur, ub, ul, lf, fr, rb, bl, df, dr, db, dl
EDGE_REFERENCE_COLORS = [
    'W',  # Edge 0 (UF): reference is White (on U)
    'W',  # Edge 1 (UR): reference is White (on U)
    'B',  # Edge 2 (UB): reference is Blue (on B, bu)
    'O',  # Edge 3 (UL): reference is Orange (on L, lu)
    'O',  # Edge 4 (FL): reference is Orange (on L, lf)
    'G',  # Edge 5 (FR): reference is Green (on F)
    'R',  # Edge 6 (BR): reference is Red (on R, rb)
    'O',  # Edge 7 (BL): reference is Orange (on L, bl)
    'G',  # Edge 8 (DF): reference is Green (on F)
    'R',  # Edge 9 (DR): reference is Red (on R)
    'B',  # Edge 10 (DB): reference is Blue (on B, db)
    'O',  # Edge 11 (DL): reference is Orange (on L, dl)
]


def faces_to_cubie_state(faces):
    """
    Convert 6x3x3 face array to cubie model state.
    
    Args:
        faces: numpy array of shape (6, 3, 3) where faces[face_idx][row][col] = color_code
    
    Returns:
        CubeState object, or None if conversion fails
    """
    # Initialize arrays
    corner_perm = np.zeros(8, dtype=np.int32)
    corner_orient = np.zeros(8, dtype=np.int32)
    edge_perm = np.zeros(12, dtype=np.int32)
    edge_orient = np.zeros(12, dtype=np.int32)
    
    # Convert color codes to letters
    color_map = {i: FACE_COLORS[i] for i in range(6)}
    
    # Find corners
    for corner_pos in range(8):
        corner_def = CORNER_DEFINITIONS[corner_pos]
        colors = []
        face_indices = []
        
        for face_idx, row, col in corner_def:
            color_code = int(faces[face_idx, row, col])
            color = color_map[color_code]
            colors.append(color)
            face_indices.append(face_idx)
        
        # Find which cubie this is
        cubie_idx, orientation = find_corner_cubie(colors, face_indices, corner_pos)
        if cubie_idx is None:
            # Debug: print which corner failed
            corner_names = ['URF', 'UFL', 'ULB', 'UBR', 'DFR', 'DLF', 'DBL', 'DRB']
            print(f"Failed to match corner {corner_names[corner_pos]} with colors {colors}")
            return None  # Invalid state
        
        corner_perm[corner_pos] = cubie_idx
        corner_orient[corner_pos] = orientation
    
    # Find edges
    for edge_pos in range(12):
        edge_def = EDGE_DEFINITIONS[edge_pos]
        colors = []
        face_indices = []
        
        for face_idx, row, col in edge_def:
            color_code = int(faces[face_idx, row, col])
            color = color_map[color_code]
            colors.append(color)
            face_indices.append(face_idx)
        
        # Find which cubie this is
        cubie_idx, orientation = find_edge_cubie(colors, face_indices, edge_pos)
        if cubie_idx is None:
            # Debug: print which edge failed
            # Paper order: uf, ur, ub, ul, lf, fr, rb, bl, df, dr, db, dl
            edge_names = ['UF', 'UR', 'UB', 'UL', 'FL', 'FR', 'BR', 'BL', 'DF', 'DR', 'DB', 'DL']
            print(f"Failed to match edge {edge_names[edge_pos]} with colors {colors}")
            return None  # Invalid state
        
        edge_perm[edge_pos] = cubie_idx
        edge_orient[edge_pos] = orientation
    
    return CubeState(corner_perm, corner_orient, edge_perm, edge_orient)


def find_corner_cubie(colors, face_indices, corner_pos):
    """
    Find which corner cubie matches the given colors and calculate orientation.
    
    Uses paper's '+' marker system: orientation is based on which face the reference
    facet (marked with +) is on. Reference facet should be on U or D face.
    
    Args:
        colors: list of 3 color letters (in order of face_indices)
        face_indices: list of 3 face indices where colors appear (U/L/F/R/B/D)
        corner_pos: the corner position (0-7) we're looking at
    
    Returns:
        (cubie_index, orientation) or (None, None) if not found
    """
    # Try each cubie
    for cubie_idx in range(8):
        solved_colors = SOLVED_CORNER_COLORS[cubie_idx]
        
        # Check if colors match (as a set, order doesn't matter for matching)
        if set(colors) != set(solved_colors):
            continue
        
        # Find the reference color for this cubie (the color on U or D in solved state)
        reference_color = CORNER_REFERENCE_COLORS[cubie_idx]
        
        # Find which face the reference color is currently on
        reference_color_idx = None
        for i, color in enumerate(colors):
            if color == reference_color:
                reference_color_idx = i
                break
        
        if reference_color_idx is None:
            continue  # Shouldn't happen if colors match
        
        # Get the face index where the reference color currently appears
        reference_face_current = face_indices[reference_color_idx]
        
        # The reference facet should be on U or D face for orientation 0
        # For this position, what face should have the reference facet?
        expected_reference_face = CORNER_REFERENCE_FACES[corner_pos]
        
        # Find which index in face_indices has the expected reference face (U or D)
        expected_ref_idx = None
        for i, face_idx in enumerate(face_indices):
            if face_idx == expected_reference_face:
                expected_ref_idx = i
                break
        
        if expected_ref_idx is None:
            continue  # Shouldn't happen - every corner position has U or D face
        
        # Find which index currently has the reference color
        ref_color_idx = None
        for i, color in enumerate(colors):
            if color == reference_color:
                ref_color_idx = i
                break
        
        if ref_color_idx is None:
            continue  # Shouldn't happen if colors match
        
        # Calculate orientation: how many positions is reference from where it should be?
        # If reference is at expected_ref_idx, orientation is 0
        # If reference is at (expected_ref_idx + 1) % 3, orientation is 1 (CW)
        # If reference is at (expected_ref_idx + 2) % 3, orientation is 2 (CCW)
        orientation = (ref_color_idx - expected_ref_idx) % 3
        
        # Verify this orientation produces correct color arrangement
        # Rotate colors by inverse orientation to check if they match solved state
        inv_orientation = (3 - orientation) % 3
        rotated_colors_check = colors[inv_orientation:] + colors[:inv_orientation]
        
        if rotated_colors_check == solved_colors:
            return cubie_idx, orientation
        
        # If no orientation worked, try matching by color order (fallback)
        for orient in range(3):
            rotated = colors[orient:] + colors[:orient]
            if rotated == solved_colors:
                return cubie_idx, orient
    
    return None, None


def find_edge_cubie(colors, face_indices, edge_pos):
    """
    Find which edge cubie matches the given colors and calculate orientation.
    
    Uses paper's '+' marker system: orientation is based on which face the reference
    facet (marked with +) is on. Reference facet should be on a specific face.
    
    Args:
        colors: list of 2 color letters (in order of face_indices)
        face_indices: list of 2 face indices where colors appear (U/L/F/R/B/D)
        edge_pos: the edge position (0-11) we're looking at
    
    Returns:
        (cubie_index, orientation) or (None, None) if not found
    """
    # Try each edge cubie
    for cubie_idx in range(12):
        solved_colors = SOLVED_EDGE_COLORS[cubie_idx]
        
        # Check if colors match (as a set, order doesn't matter for matching)
        if set(colors) != set(solved_colors):
            continue
        
        # Find the reference color for this cubie (the color on the reference face)
        reference_color = EDGE_REFERENCE_COLORS[cubie_idx]
        
        # Find which face the reference color is currently on
        ref_color_idx = None
        for i, color in enumerate(colors):
            if color == reference_color:
                ref_color_idx = i
                break
        
        if ref_color_idx is None:
            continue  # Shouldn't happen if colors match
        
        # Get the face index where the reference color currently appears
        reference_face_current = face_indices[ref_color_idx]
        
        # The reference facet should be on a specific face for this position
        expected_reference_face = EDGE_POSITION_REFERENCE_FACES[edge_pos]
        
        # Calculate orientation: 0 if reference is on expected face, 1 if flipped
        if reference_face_current == expected_reference_face:
            orientation = 0
        else:
            orientation = 1
        
        # Verify this orientation produces correct color arrangement
        # The orientation we calculated should be correct, but verify by checking colors
        # If orientation is 0, colors should match solved_colors
        # If orientation is 1, colors should match solved_colors reversed
        if orientation == 0:
            if colors == solved_colors:
                return cubie_idx, orientation
            # If colors are reversed, orientation should be 1
            elif colors == solved_colors[::-1]:
                return cubie_idx, 1
        else:  # orientation == 1
            if colors == solved_colors[::-1]:
                return cubie_idx, orientation
            # If colors match solved, orientation should be 0
            elif colors == solved_colors:
                return cubie_idx, 0
    
    return None, None


def cubie_state_to_faces(state: CubeState):
    """
    Convert cubie model state to 6x3x3 face array.
    
    Args:
        state: CubeState object
    
    Returns:
        numpy array of shape (6, 3, 3) with color codes
    """
    faces = np.zeros((6, 3, 3), dtype=int)
    
    # We need to map cubies back to face positions
    # This requires applying the inverse permutation
    
    # For corners
    for pos in range(8):
        cubie = state.corner_perm[pos]
        orient = state.corner_orient[pos]
        corner_def = CORNER_DEFINITIONS[pos]
        solved_colors = SOLVED_CORNER_COLORS[cubie]
        
        # New orientation system based on paper's '+' markers:
        # Orientation 0: reference facet (marked with +) is on U or D face
        # Orientation 1: reference facet rotated clockwise to a side face  
        # Orientation 2: reference facet rotated counterclockwise to a side face
        # 
        # The reference facet is always the first color in solved_colors (U or D color)
        # We need to rotate the colors so the reference facet ends up on the correct face
        
        # Expected face for reference facet at this position (U or D)
        expected_ref_face = CORNER_REFERENCE_FACES[pos]
        
        # Find which position in corner_def has the expected reference face
        ref_face_idx = None
        for i, (face_idx, row, col) in enumerate(corner_def):
            if face_idx == expected_ref_face:
                ref_face_idx = i
                break
        
        if ref_face_idx is None:
            # Shouldn't happen - every corner position has U or D face
            ref_face_idx = 0
        
        # The reference color (solved_colors[0]) should be at ref_face_idx when orient=0
        # With orientation, the reference rotates:
        # orient=0: reference at ref_face_idx (no rotation from base)
        # orient=1: reference rotated CW from ref_face_idx -> at (ref_face_idx + 1) % 3
        # orient=2: reference rotated CCW from ref_face_idx -> at (ref_face_idx + 2) % 3
        
        # Calculate where reference should be with this orientation
        target_ref_idx = (ref_face_idx + orient) % 3
        
        # Rotate colors so reference (index 0) goes to target_ref_idx
        rotation = (3 - target_ref_idx) % 3
        rotated_colors = solved_colors[rotation:] + solved_colors[:rotation]
        
        # Place colors on faces
        for i, (face_idx, row, col) in enumerate(corner_def):
            color = rotated_colors[i]
            color_code = FACE_COLORS.index(color)
            faces[face_idx, row, col] = color_code
    
    # For edges
    for pos in range(12):
        cubie = state.edge_perm[pos]
        orient = state.edge_orient[pos]
        edge_def = EDGE_DEFINITIONS[pos]
        solved_colors = SOLVED_EDGE_COLORS[cubie]
        
        # New orientation system based on paper's '+' markers:
        # Orientation 0: reference facet (marked with +) is on the correct face
        # Orientation 1: reference facet is flipped to the other face
        #
        # The reference facet is the one with the reference color
        # We need to place it on the correct face based on orientation
        
        # Expected face for reference facet at this position
        expected_ref_face = EDGE_POSITION_REFERENCE_FACES[pos]
        
        # Find which position in edge_def has the expected reference face
        ref_face_idx = None
        for i, (face_idx, row, col) in enumerate(edge_def):
            if face_idx == expected_ref_face:
                ref_face_idx = i
                break
        
        if ref_face_idx is None:
            # Shouldn't happen - every edge position has both faces defined
            ref_face_idx = 0
        
        # Get the reference color for this cubie
        reference_color = EDGE_REFERENCE_COLORS[cubie]
        
        # Find which position in solved_colors has the reference color
        ref_color_idx = None
        for i, color in enumerate(solved_colors):
            if color == reference_color:
                ref_color_idx = i
                break
        
        if ref_color_idx is None:
            # Shouldn't happen
            ref_color_idx = 0
        
        # If orientation is 0, reference should be at ref_face_idx
        # If orientation is 1, reference should be at the other position
        if orient == 0:
            # Reference at ref_face_idx: place reference color at ref_face_idx
            if ref_color_idx == ref_face_idx:
                colors = solved_colors
            else:
                colors = solved_colors[::-1]
        else:  # orient == 1
            # Reference flipped: place reference color at the other position
            if ref_color_idx == ref_face_idx:
                colors = solved_colors[::-1]
            else:
                colors = solved_colors
        
        # Place colors on faces
        for i, (face_idx, row, col) in enumerate(edge_def):
            color = colors[i]
            color_code = FACE_COLORS.index(color)
            faces[face_idx, row, col] = color_code
    
    # Set center facelets (each face's center is always that face's color)
    # U=W(0), L=O(3), F=G(5), R=R(2), B=B(4), D=Y(1)
    center_colors = [0, 3, 5, 2, 4, 1]  # U, L, F, R, B, D
    for face_idx in range(6):
        faces[face_idx, 1, 1] = center_colors[face_idx]
    
    return faces

