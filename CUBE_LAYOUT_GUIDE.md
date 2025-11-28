# Cube Layout Guide - Understanding the 2D Net View

## Overview

The GUI displays the Rubik's Cube as a **2D net** (unfolded view) of all 6 faces. This is like "unfolding" a cube and laying it flat.

## Layout Structure

The net is arranged in a **cross pattern**:

```
        [U] (Up)
[L] [F] [R] [B]  (Left, Front, Right, Back)
        [D] (Down)
```

### Visual Layout:

```
Row 0:        [U]        (Up face - top center)
Row 1:  [L] [F] [R] [B]  (Left, Front, Right, Back - middle row)
Row 2:        [D]        (Down face - bottom center)
```

## How to Read the Layout

### Face Positions:
- **U (Up)**: Top face - White in standard solved state
- **L (Left)**: Left face - Orange in standard solved state
- **F (Front)**: Front face - Green in standard solved state
- **R (Right)**: Right face - Red in standard solved state
- **B (Back)**: Back face - Blue in standard solved state
- **D (Down)**: Bottom face - Yellow in standard solved state

### Each Face is a 3×3 Grid:
Each face shows 9 small squares (facelets):
```
[1] [2] [3]
[4] [5] [6]
[7] [8] [9]
```

## How to Input Colors

### Method 1: Click Individual Facelets (Manual)
1. **Select a color** from the color buttons (W, Y, R, O, B, G)
2. **Click on any facelet** (small square) in the cube net
3. That facelet will change to the selected color
4. Repeat for all facelets you want to change

**Important**: This method is error-prone! It's easy to create invalid configurations.

### Method 2: Load from Scramble (Recommended)
1. Click **"Load from Scramble"** button
2. Enter moves like: `U R F2 D L B'`
3. Click **"Apply"**
4. The cube will be automatically scrambled and displayed correctly

**This is the recommended method** because it guarantees a valid cube state.

## Understanding the 3D to 2D Mapping

### Standard Cube Orientation:
- **White (W)** = Up face
- **Yellow (Y)** = Down face
- **Green (G)** = Front face
- **Blue (B)** = Back face
- **Red (R)** = Right face
- **Orange (O)** = Left face

### How Faces Connect:
When you look at the net:
- The **top edge** of F connects to the **bottom edge** of U
- The **bottom edge** of F connects to the **top edge** of D
- The **right edge** of F connects to the **left edge** of R
- The **left edge** of F connects to the **right edge** of L
- The **right edge** of U connects to the **top edge** of R
- The **left edge** of U connects to the **top edge** of L
- And so on...

## Example: Solved State

In a solved state, each face should be all one color:
- **U face**: All white (W)
- **L face**: All orange (O)
- **F face**: All green (G)
- **R face**: All red (R)
- **B face**: All blue (B)
- **D face**: All yellow (Y)

## Tips for Manual Input

If you want to manually set colors (not recommended):

1. **Start with solved state**: Click "Reset to Solved"
2. **Understand corner pieces**: Each corner has 3 colors from 3 different faces
3. **Understand edge pieces**: Each edge has 2 colors from 2 different faces
4. **Be careful**: It's very easy to create an invalid configuration

**Better approach**: Always use "Load from Scramble" to create valid states!

## Visual Example

When you see the GUI, imagine you're looking at an unfolded cube:

```
        ┌───┬───┬───┐
        │ U │ U │ U │  ← Up face (White when solved)
        ├───┼───┼───┤
        │ U │ U │ U │
        ├───┼───┼───┤
        │ U │ U │ U │
┌───┬───┼───┼───┼───┼───┬───┐
│ L │ L │ F │ F │ R │ R │ B │ B │
├───┼───┼───┼───┼───┼───┼───┼───┤
│ L │ L │ F │ F │ R │ R │ B │ B │
├───┼───┼───┼───┼───┼───┼───┼───┤
│ L │ L │ F │ F │ R │ R │ B │ B │
└───┴───┼───┼───┼───┼───┴───┘
        │ D │ D │ D │
        ├───┼───┼───┤
        │ D │ D │ D │  ← Down face (Yellow when solved)
        ├───┼───┼───┤
        │ D │ D │ D │
        └───┴───┴───┘
```

Each small square is a **facelet** that you can click to change its color.

