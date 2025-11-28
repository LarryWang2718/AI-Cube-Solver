"""
Utility functions for cube manipulation.
"""

import random
from cube_state import CubeState
from moves import MOVE_TABLE, MOVE_NAMES


def apply_moves(state: CubeState, move_names: list) -> CubeState:
    """
    Apply a sequence of moves to a state.
    
    Args:
        state: initial cube state
        move_names: list of move names (e.g., ['U', "R'", 'F2'])
    
    Returns:
        New state after applying moves
    """
    current_state = state.copy()
    for move_name in move_names:
        if move_name in MOVE_TABLE:
            current_state = MOVE_TABLE[move_name].apply(current_state)
        else:
            raise ValueError(f"Unknown move: {move_name}")
    return current_state


def scramble(state: CubeState, num_moves: int = 25, seed: int = None) -> tuple:
    """
    Scramble the cube by applying random moves.
    
    Args:
        state: initial state (usually solved)
        num_moves: number of random moves to apply
        seed: random seed for reproducibility
    
    Returns:
        (scrambled_state, move_sequence) tuple
    """
    if seed is not None:
        random.seed(seed)
    
    move_sequence = []
    current_state = state.copy()
    last_move = None
    
    for _ in range(num_moves):
        # Choose a random move that's not the inverse of the last move
        available_moves = [m for m in MOVE_NAMES 
                          if m != last_move or last_move is None]
        move_name = random.choice(available_moves)
        
        move_sequence.append(move_name)
        current_state = MOVE_TABLE[move_name].apply(current_state)
        last_move = move_name
    
    return current_state, move_sequence


def format_solution(move_sequence: list) -> str:
    """Format a solution as a readable string."""
    if not move_sequence:
        return "No moves needed (already solved)"
    return " ".join(move_sequence)


def verify_solution(initial_state: CubeState, solution: list) -> bool:
    """
    Verify that a solution actually solves the cube.
    
    Args:
        initial_state: the scrambled state
        solution: list of move names
    
    Returns:
        True if solution is correct, False otherwise
    """
    final_state = apply_moves(initial_state, solution)
    return final_state.is_solved()

