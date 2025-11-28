"""
Basic tests to verify the cube solver implementation.
"""

from cube_state import CubeState, solved_state
from moves import MOVE_TABLE, ALL_MOVES
from utils import apply_moves, verify_solution


def test_solved_state():
    """Test that solved state is actually solved."""
    state = solved_state()
    assert state.is_solved(), "Solved state should be solved"
    assert state.is_valid(), "Solved state should be valid"
    print("✓ Solved state test passed")


def test_move_application():
    """Test that moves can be applied."""
    state = solved_state()
    
    # Apply U move
    state = MOVE_TABLE['U'].apply(state)
    assert not state.is_solved(), "After U move, cube should not be solved"
    assert state.is_valid(), "State after move should be valid"
    
    # Apply U' to undo
    state = MOVE_TABLE["U'"].apply(state)
    assert state.is_solved(), "After U U', cube should be solved"
    print("✓ Move application test passed")


def test_move_sequence():
    """Test applying a sequence of moves."""
    state = solved_state()
    
    # Apply U R U' R'
    moves = ['U', 'R', "U'", "R'"]
    state = apply_moves(state, moves)
    assert state.is_solved(), "U R U' R' should return to solved"
    print("✓ Move sequence test passed")


def test_scramble_solve():
    """Test that a simple scramble can be solved."""
    state = solved_state()
    
    # Simple 2-move scramble
    scramble_moves = ['U', 'R']
    scrambled = apply_moves(state, scramble_moves)
    
    # Solution should be R' U'
    solution = ["R'", "U'"]
    assert verify_solution(scrambled, solution), "Solution should work"
    print("✓ Scramble-solve test passed")


def test_heuristic_basic():
    """Test that heuristics can be computed."""
    from heuristics import Heuristic
    
    state = solved_state()
    heuristic = Heuristic()
    
    h = heuristic.h(state)
    assert h == 0, "Solved state should have heuristic 0"
    print("✓ Heuristic test passed (solved state)")
    
    # Apply one move
    state = MOVE_TABLE['U'].apply(state)
    h = heuristic.h(state)
    assert h >= 0, "Heuristic should be non-negative"
    print(f"  Heuristic after U move: {h:.1f}")


if __name__ == '__main__':
    print("Running basic tests...")
    print()
    
    test_solved_state()
    test_move_application()
    test_move_sequence()
    test_scramble_solve()
    test_heuristic_basic()
    
    print()
    print("All basic tests passed!")

