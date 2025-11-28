# GUI User Guide

## Getting Started

Launch the GUI:
```bash
python run_gui.py
```

## Interface Overview

The GUI displays:
- **Cube Net View**: A 2D unfolded view of all 6 faces (U, L, F, R, B, D)
- **Color Picker**: Buttons to select colors (W=White, Y=Yellow, R=Red, O=Orange, B=Blue, G=Green)
- **Control Buttons**: Reset, Load Scramble, Solve, Animate Solution
- **Status Bar**: Shows current operation status
- **Solution Display**: Shows the found solution

## How to Use

### Method 1: Load from Scramble (Recommended)

1. Click **"Load from Scramble"**
2. Enter scramble moves (e.g., `U R F2 D L B'`)
3. Click **"Apply"**
4. The cube will be displayed in the scrambled state
5. Click **"Solve"** to find a solution
6. Click **"Animate Solution"** to watch the solving steps

### Method 2: Manual Color Setting

1. Select a color from the color picker buttons
2. Click on any facelet (small square) in the cube net to change its color
3. Repeat until the cube is configured
4. Click **"Solve"** to find a solution

**Note**: Manual color setting requires a valid cube configuration. Invalid configurations will show an error.

### Method 3: Start from Solved

1. Click **"Reset to Solved"** to start with a solved cube
2. Use **"Load from Scramble"** to scramble it
3. Then solve it

## Tips

- **For best results**: Use "Load from Scramble" rather than manual color setting
- **First run**: Pattern databases will be built automatically (takes 1-2 minutes)
- **Solving time**: Typically 1-5 seconds for random scrambles
- **Animation speed**: Adjustable in code (default 0.8 seconds per move)

## Troubleshooting

**"Could not convert cube state"**
- The cube configuration may be invalid
- Try using "Load from Scramble" instead
- Make sure each face has 9 facelets of the same color in solved state

**"Invalid cube state"**
- The configuration violates physical constraints
- This can happen with manually set colors
- Use "Reset to Solved" and then "Load from Scramble"

**GUI is slow**
- First run builds pattern databases (normal, takes time)
- Subsequent runs are much faster

## Color Scheme

Standard Rubik's Cube colors:
- **W** (White) - Up face
- **Y** (Yellow) - Down face  
- **R** (Red) - Front face
- **O** (Orange) - Back face
- **B** (Blue) - Right face
- **G** (Green) - Left face

## Example Workflow

1. Launch GUI: `python run_gui.py`
2. Click "Load from Scramble"
3. Enter: `U R F2 D L`
4. Click "Apply"
5. Click "Solve" (wait for solution)
6. Click "Animate Solution" to watch it solve!

