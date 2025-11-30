"""
Interactive script to explore and understand move table encoding.
Run this to see how moves are encoded and applied.
"""

from cube_state import solved_state
from cube_converter import cubie_state_to_faces, FACE_COLORS
from moves import MOVE_TABLE

def print_corner_info(corner_idx, corner_name):
    """Print information about a corner position."""
    print(f"\n  Corner {corner_idx} ({corner_name}):")
    print(f"    Position in cube: {corner_name}")

def print_edge_info(edge_idx, edge_name):
    """Print information about an edge position."""
    print(f"\n  Edge {edge_idx} ({edge_name}):")
    print(f"    Position in cube: {edge_name}")

def explore_move(move_name):
    """Explore a specific move in detail."""
    if move_name not in MOVE_TABLE:
        print(f"Unknown move: {move_name}")
        return
    
    move = MOVE_TABLE[move_name]
    print(f"\n{'='*60}")
    print(f"EXPLORING MOVE: {move_name}")
    print(f"{'='*60}")
    
    # Corner information
    print("\n📦 CORNER PERMUTATION:")
    print(f"  corner_perm = {list(move.corner_perm)}")
    print("\n  What this means:")
    # Corner names match new labeling (picture vertices 1-8, 0-indexed here)
    corner_names = ['DFR', 'DRB', 'URF', 'UBR', 'UFL', 'ULB', 'DLF', 'DBL']
    for i, target in enumerate(move.corner_perm):
        if i != target:
            print(f"    Position {i} ({corner_names[i]}) → Position {target} ({corner_names[target]})")
    
    print("\n📐 CORNER ORIENTATION DELTA:")
    print(f"  corner_orient_delta = {list(move.corner_orient_delta)}")
    print("\n  What this means:")
    for i, delta in enumerate(move.corner_orient_delta):
        if delta != 0:
            twist = "clockwise" if delta == 1 else "counterclockwise"
            print(f"    Position {i} ({corner_names[i]}): twists {delta} ({twist})")
    
    # Edge information
    print("\n📏 EDGE PERMUTATION:")
    print(f"  edge_perm = {list(move.edge_perm)}")
    print("\n  What this means:")
    edge_names = ['UR', 'UF', 'UL', 'UB', 'DR', 'DF', 'DL', 'DB', 'FR', 'FL', 'BL', 'BR']
    for i, target in enumerate(move.edge_perm):
        if i != target:
            print(f"    Position {i} ({edge_names[i]}) → Position {target} ({edge_names[target]})")
    
    print("\n🔄 EDGE ORIENTATION DELTA:")
    print(f"  edge_orient_delta = {list(move.edge_orient_delta)}")
    print("\n  What this means:")
    for i, delta in enumerate(move.edge_orient_delta):
        if delta != 0:
            print(f"    Position {i} ({edge_names[i]}): flips")
    
    # Apply move to solved state
    print("\n🧪 TESTING ON SOLVED STATE:")
    solved = solved_state()
    new_state = move.apply(solved)
    
    # Check if still solved
    if new_state.is_solved():
        print("  ✓ Move returns to solved state (this is U2, D2, etc.)")
    else:
        print("  ✗ Move scrambles the cube")
        print(f"  Corner permutation: {list(new_state.corner_perm)}")
        print(f"  Edge permutation: {list(new_state.edge_perm)}")

def show_permutation_cycle(perm, names):
    """Show the cycles in a permutation."""
    visited = set()
    cycles = []
    
    for start in range(len(perm)):
        if start in visited:
            continue
        
        cycle = []
        current = start
        while current not in visited:
            visited.add(current)
            cycle.append(current)
            current = perm[current]
        
        if len(cycle) > 1:
            cycles.append(cycle)
    
    if cycles:
        print("  Cycles:")
        for cycle in cycles:
            cycle_names = [names[i] for i in cycle]
            print(f"    ({' → '.join(cycle_names)} → {cycle_names[0]})")
    else:
        print("  (No cycles - identity permutation)")

def compare_moves():
    """Compare different moves to see patterns."""
    print("\n" + "="*60)
    print("COMPARING MOVES: U vs F")
    print("="*60)
    
    u_move = MOVE_TABLE['U']
    f_move = MOVE_TABLE['F']
    
    # Corner names match new labeling (picture vertices 1-8, 0-indexed here)
    corner_names = ['DFR', 'DRB', 'URF', 'UBR', 'UFL', 'ULB', 'DLF', 'DBL']
    edge_names = ['UR', 'UF', 'UL', 'UB', 'DR', 'DF', 'DL', 'DB', 'FR', 'FL', 'BL', 'BR']
    
    print("\nU MOVE:")
    print("  Corner permutation cycles:")
    show_permutation_cycle(u_move.corner_perm, corner_names)
    print(f"  Corner orientation changes: {sum(u_move.corner_orient_delta)} (should be 0 mod 3)")
    print("  Edge permutation cycles:")
    show_permutation_cycle(u_move.edge_perm, edge_names)
    print(f"  Edge orientation changes: {sum(f_move.edge_orient_delta)} (should be 0 mod 2)")
    
    print("\nF MOVE:")
    print("  Corner permutation cycles:")
    show_permutation_cycle(f_move.corner_perm, corner_names)
    print(f"  Corner orientation changes: {sum(f_move.corner_orient_delta)} (should be 0 mod 3)")
    print("  Edge permutation cycles:")
    show_permutation_cycle(f_move.edge_perm, edge_names)
    print(f"  Edge orientation changes: {sum(f_move.edge_orient_delta)} (should be 0 mod 2)")

def demonstrate_application():
    """Demonstrate how a move is applied step by step."""
    print("\n" + "="*60)
    print("STEP-BY-STEP: Applying U Move")
    print("="*60)
    
    solved = solved_state()
    move = MOVE_TABLE['U']
    
    print("\n1. Initial state (solved):")
    print(f"   corner_perm = {list(solved.corner_perm)}")
    print(f"   corner_orient = {list(solved.corner_orient)}")
    
    print("\n2. Move definition:")
    print(f"   corner_perm = {list(move.corner_perm)}")
    print(f"   corner_orient_delta = {list(move.corner_orient_delta)}")
    
    print("\n3. Compute inverse permutation:")
    import numpy as np
    corner_perm_inv = np.argsort(move.corner_perm)
    print(f"   corner_perm_inv = {list(corner_perm_inv)}")
    print("   (This tells us where each cubie came from)")
    
    print("\n4. Apply permutation:")
    new_corner_perm = solved.corner_perm[corner_perm_inv]
    print(f"   new_corner_perm = {list(new_corner_perm)}")
    print("   (For each position i, we look up which cubie came from corner_perm_inv[i])")
    
    print("\n5. Apply orientation:")
    new_corner_orient = (solved.corner_orient[corner_perm_inv] + 
                        move.corner_orient_delta) % 3
    print(f"   new_corner_orient = {list(new_corner_orient)}")
    print("   (Old orientation + delta, mod 3)")
    
    print("\n6. Final state after U move:")
    final_state = move.apply(solved)
    print(f"   corner_perm = {list(final_state.corner_perm)}")
    print(f"   corner_orient = {list(final_state.corner_orient)}")

if __name__ == "__main__":
    print("MOVE TABLE EXPLORATION TOOL")
    print("="*60)
    
    # Explore a simple move
    explore_move('U')
    
    # Explore a complex move
    explore_move('F')
    
    # Compare moves
    compare_moves()
    
    # Step-by-step demonstration
    demonstrate_application()
    
    print("\n" + "="*60)
    print("Try exploring other moves:")
    print("  explore_move('R')")
    print("  explore_move('L')")
    print("  explore_move('B')")
    print("="*60)

