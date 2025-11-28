# Quick Start Guide

## Installation

1. Install the required dependency:
```bash
pip install numpy
```

Or using the requirements file:
```bash
pip install -r requirements.txt
```

## Running the Solver

### Basic Usage

Solve a randomly scrambled cube (25 moves by default):
```bash
python main.py
```

### Common Examples

**Solve with a custom scramble:**
```bash
python main.py --moves "U R F2 D L B' U2"
```

**Solve with a specific number of random moves:**
```bash
python main.py --scramble 15
```

**Use a reproducible random scramble (with seed):**
```bash
python main.py --scramble 20 --seed 42
```

**Use IDDFS algorithm instead of IDA*:**
```bash
python main.py --algorithm iddfs --max-depth 15
```

**Limit IDA* iterations (for faster testing):**
```bash
python main.py --moves "U R" --max-iterations 10
```

## What to Expect

### First Run
- The pattern databases will be built automatically (takes 1-2 minutes)
- You'll see progress messages for each PDB being built
- Corner Permutation PDB may only reach ~12.5% coverage (this is normal and still works)

### Subsequent Runs
- Much faster since PDBs are already in memory
- Typical solve time: 1-5 seconds for random scrambles
- Solution length: usually 15-25 moves for random scrambles

## Example Output

```
============================================================
3x3x3 Rubik's Cube Solver
============================================================

Scrambling cube with 25 random moves...
Scramble: U R F2 D L B' U2 R' F D2 L2 B R F' D L' B2 R' F D' L B R' F D

Using IDA* algorithm with pattern databases...

Building pattern databases...
Building Corner Orientation PDB...
  ...
Corner Orientation PDB built: 2187/2187 states
Building Edge Orientation PDB...
  ...
Edge Orientation PDB built: 2048/2048 states
Building Corner Permutation PDB...
  ...
Corner Permutation PDB built: 5040/40320 states

Initial heuristic value: 18.0
Starting IDA* search...
Iteration 1: threshold = 18.0
Iteration 2: threshold = 19.0
...
Solution found! Expanded 12345 nodes

============================================================
Solution found (22 moves):
  R' D L' B2 R F' D' L B R' F D L' B2 R F' D' L B R' F D

Statistics:
  Nodes expanded: 12,345
  Time: 3.45 seconds
  Nodes/second: 3,578

Verifying solution...
Solution is correct!
============================================================
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'numpy'"**
- Run: `python -m pip install numpy`

**Solution seems incorrect**
- The solver finds optimal solutions in the quarter-turn metric
- Verify the solution by checking if it actually solves the cube
- Try a simpler scramble first (e.g., `--moves "U R"`)

**Very slow performance**
- This is normal for the first run (building PDBs)
- For faster testing, use `--max-iterations 10` or simpler scrambles
- IDDFS is slower than IDA* for most cases

