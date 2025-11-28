# 3×3×3 Rubik's Cube Solver

An AI agent that solves the Rubik's Cube using IDA* search with pattern database heuristics, as described in the formal model specification.

## Features

- **Cubie-based state representation**: Models the cube using corner and edge permutations and orientations
- **Pattern Database Heuristics**: 
  - Corner Orientation PDB (3^7 = 2,187 states)
  - Edge Orientation PDB (2^11 = 2,048 states)
  - Corner Permutation PDB (8! = 40,320 states)
- **Search Algorithms**:
  - IDDFS (Iterative Deepening DFS) - baseline
  - IDA* (Iterative Deepening A*) - main algorithm with admissible heuristics
- **Move pruning**: Avoids immediate inverse moves to reduce branching factor

## Installation

Requires Python 3.7+ and numpy:

```bash
pip install numpy
```

## Usage

### GUI Interface (Recommended)

Launch the visual interface:

```bash
python run_gui.py
```

Or:

```bash
python cube_gui.py
```

Features:
- **Visual cube representation** in 2D net format
- **Color picker** to customize cube colors
- **Load from scramble** - enter moves to scramble the cube
- **Solve** - automatically find solution using IDA*
- **Animate solution** - watch the solving steps

### Command Line Interface

Solve a randomly scrambled cube:

```bash
python main.py
```

### Command Line Options

```bash
python main.py --help
```

Options:
- `--algorithm {iddfs,idastar}`: Choose search algorithm (default: idastar)
- `--scramble N`: Number of random moves for scrambling (default: 25)
- `--seed N`: Random seed for reproducible scrambles
- `--moves "U R F2 ..."`: Custom scramble as space-separated moves
- `--max-depth N`: Maximum depth for IDDFS (default: 20)
- `--max-iterations N`: Maximum iterations for IDA* (default: 50)

### Examples

Solve with a specific scramble:
```bash
python main.py --moves "U R F2 D L B' U2"
```

Solve with reproducible random scramble:
```bash
python main.py --scramble 20 --seed 42
```

Use IDDFS instead of IDA*:
```bash
python main.py --algorithm iddfs --max-depth 15
```

## Architecture

- `cube_state.py`: Cube state representation using cubie model
- `moves.py`: Move definitions and application logic
- `pattern_databases.py`: PDB construction using reverse BFS
- `heuristics.py`: Heuristic functions using pattern databases
- `search.py`: IDDFS and IDA* search algorithms
- `utils.py`: Utility functions (scrambling, move application, verification)
- `main.py`: Command-line interface

## Algorithm Details

The solver implements the formal model described in the specification:

1. **State Space**: Cubie model with corner/edge permutations and orientations
2. **Move Set**: 18 moves in quarter-turn metric (QTM)
3. **Heuristics**: Pattern databases built via reverse BFS from solved state
4. **Search**: IDA* with f(n) = g(n) + h(n) where h(n) = max(h_co, h_eo, h_cp)

## Performance

- Pattern databases are built on first run (may take a few minutes)
- IDA* typically finds optimal solutions for random scrambles
- IDDFS is slower but useful for validation

## Notes

- The pattern databases are built in memory and not saved by default
- For very deep scrambles (>20 moves), IDA* may take significant time
- The implementation follows the mathematical specification closely

