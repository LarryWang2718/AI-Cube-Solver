"""
Simple example of using the cube solver.
"""

from cube_state import solved_state
from heuristics import Heuristic
from search import IDAStar
from utils import scramble, format_solution

# Create a scrambled cube
print("Creating a scrambled cube...")
initial_state, scramble_moves = scramble(solved_state(), num_moves=10, seed=42)
print(f"Scramble: {format_solution(scramble_moves)}")
print()

# Build heuristics (this will take a few minutes on first run)
print("Building pattern databases (this may take a few minutes)...")
heuristic = Heuristic()
print()

# Solve using IDA*
print("Solving with IDA*...")
solver = IDAStar(heuristic)
solution = solver.solve(initial_state)

if solution:
    print(f"\nSolution found: {format_solution(solution)}")
    print(f"Solution length: {len(solution)} moves")
    print(f"Nodes expanded: {solver.nodes_expanded:,}")
else:
    print("\nNo solution found")

