"""
Main interface for the Rubik's Cube solver.
"""

import argparse
import time
from cube_state import CubeState, solved_state
from heuristics import Heuristic
from search import IDAStar
from utils import scramble, apply_moves, format_solution, verify_solution


def main():
    parser = argparse.ArgumentParser(
        description='3x3x3 Rubik\'s Cube Solver using IDA* with Pattern Databases'
    )
    parser.add_argument('--scramble', type=int, default=25,
                       help='Number of random moves for scrambling (default: 25)')
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for scrambling (for reproducibility)')
    parser.add_argument('--moves', type=str, default=None,
                       help='Custom scramble as space-separated moves (e.g., "U R F2")')
    parser.add_argument('--max-iterations', type=int, default=50,
                       help='Maximum iterations for IDA* (default: 50)')
    parser.add_argument('--save-pdb', action='store_true',
                       help='Save pattern databases to disk (not implemented)')
    parser.add_argument('--load-pdb', type=str, default=None,
                       help='Load pattern databases from disk (not implemented)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("3x3x3 Rubik's Cube Solver")
    print("=" * 60)
    print()
    
    # Create initial state
    if args.moves:
        # Use custom scramble
        move_names = args.moves.split()
        print(f"Applying custom scramble: {format_solution(move_names)}")
        initial_state = apply_moves(solved_state(), move_names)
        scramble_moves = move_names
    else:
        # Random scramble
        print(f"Scrambling cube with {args.scramble} random moves...")
        if args.seed is not None:
            print(f"  (seed: {args.seed})")
        initial_state, scramble_moves = scramble(
            solved_state(), args.scramble, args.seed
        )
        print(f"Scramble: {format_solution(scramble_moves)}")
    
    print()
    
    # Check if already solved
    if initial_state.is_solved():
        print("Cube is already solved!")
        return
    
    # Verify state is valid
    if not initial_state.is_valid():
        print("WARNING: Initial state does not satisfy physical constraints!")
        print("This should not happen with a valid scramble.")
        return
    
    # Solve
    start_time = time.time()
    
    print("Using IDA* algorithm with pattern databases...")
    print()
    
    # Build or load heuristics
    if args.load_pdb:
        print(f"Loading pattern databases from {args.load_pdb}...")
        # TODO: Implement PDB loading
        heuristic = Heuristic()
    else:
        heuristic = Heuristic()
    
    solver = IDAStar(heuristic)
    solution = solver.solve(initial_state, args.max_iterations)
    nodes_expanded = solver.nodes_expanded
    
    if args.save_pdb:
        print("Saving pattern databases...")
        # TODO: Implement PDB saving
    
    elapsed_time = time.time() - start_time
    
    print()
    print("=" * 60)
    
    if solution:
        print(f"Solution found ({len(solution)} moves):")
        print(f"  {format_solution(solution)}")
        print()
        print(f"Statistics:")
        print(f"  Nodes expanded: {nodes_expanded:,}")
        print(f"  Time: {elapsed_time:.2f} seconds")
        print(f"  Nodes/second: {nodes_expanded / elapsed_time:,.0f}")
        
        # Verify solution
        print()
        print("Verifying solution...")
        if verify_solution(initial_state, solution):
            print("Solution is correct!")
        else:
            print("ERROR: Solution verification failed!")
    else:
        print("No solution found within limits.")
        print(f"  Nodes expanded: {nodes_expanded:,}")
        print(f"  Time: {elapsed_time:.2f} seconds")
    
    print("=" * 60)


if __name__ == '__main__':
    main()

