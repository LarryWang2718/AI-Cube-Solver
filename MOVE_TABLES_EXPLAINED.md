# Move Tables Explained: A Complete Walkthrough

## Overview

The Rubik's Cube state is encoded using the **cubie model**, which tracks:
- **8 corner cubies** (each has 3 colors)
- **12 edge cubies** (each has 2 colors)

Each move is represented by **4 arrays** that describe how the move transforms the cube state.

---

## The Four Arrays Explained

### 1. `corner_perm` (Corner Permutation)
**What it means:** Where each corner cubie moves to.

**Encoding:** `corner_perm[i] = j` means "the cubie that was at position `i` moves to position `j`"

**Example for U move:**
```python
corner_perm = [0, 1, 4, 2, 5, 3, 6, 7]
```

This means:
- Position 2 (URF) → Position 4 (UFL)
- Position 4 (UFL) → Position 5 (ULB)
- Position 5 (ULB) → Position 3 (UBR)
- Position 3 (UBR) → Position 2 (URF)
- Positions 0, 1, 6, 7 stay the same (bottom corners don't move)

**Corner positions (0-7):**
```
0: DFR (Down-Front-Right)
1: DRB (Down-Right-Back)
2: URF (Up-Right-Front)
3: UBR (Up-Back-Right)
4: UFL (Up-Front-Left)
5: ULB (Up-Left-Back)
6: DLF (Down-Left-Front)
7: DBL (Down-Back-Left)
```

### 2. `corner_orient_delta` (Corner Orientation Change)
**What it means:** How much each corner twists (0, 1, or 2).

**Encoding:** `corner_orient_delta[i]` is added to the orientation at position `i` after the move (mod 3).

**Values:**
- `0` = no twist
- `1` = twist clockwise
- `2` = twist counterclockwise

**Example for F move:**
```python
corner_orient_delta = [1, 2, 0, 0, 2, 1, 0, 0]
```

This means:
- Position 0 (URF): twists by 1 (clockwise)
- Position 1 (UFL): twists by 2 (counterclockwise)
- Position 4 (DFR): twists by 2 (counterclockwise)
- Position 5 (DLF): twists by 1 (clockwise)
- Others: no twist

**Why corners twist:** When you rotate a face, corners that move to a different face orientation get twisted because their colors are now on different faces.

### 3. `edge_perm` (Edge Permutation)
**What it means:** Where each edge cubie moves to.

**Encoding:** `edge_perm[i] = j` means "the cubie that was at position `i` moves to position `j`"

**Example for U move:**
```python
edge_perm = [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11]
```

This means:
- Position 0 (UF) → Position 1 (UR)
- Position 1 (UR) → Position 2 (UB)
- Position 2 (UB) → Position 3 (UL)
- Position 3 (UL) → Position 0 (UF)
- Positions 4-11 stay the same (middle and bottom edges don't move)

**Edge positions (0-11):**
```
0: UF (Up-Front)
1: UR (Up-Right)
2: UB (Up-Back)
3: UL (Up-Left)
4: FL (Front-Left)
5: FR (Front-Right)
6: BR (Back-Right)
7: BL (Back-Left)
8: DF (Down-Front)
9: DR (Down-Right)
10: DB (Down-Back)
11: DL (Down-Left)
```

### 4. `edge_orient_delta` (Edge Orientation Change)
**What it means:** Whether each edge flips (0 or 1).

**Encoding:** `edge_orient_delta[i]` is added to the orientation at position `i` after the move (mod 2).

**Values:**
- `0` = no flip
- `1` = flip

**Example for F move:**
```python
edge_orient_delta = [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0]
```

This means:
- Position 1 (UF): flips
- Position 5 (DF): flips
- Position 8 (FR): flips
- Position 9 (FL): flips
- Others: no flip

**Why edges flip:** When you rotate a face, edges that move to a different face orientation get flipped because their colors are now on different faces.

---

## How Moves Are Applied

When you apply a move `m` to a state `s`, you get a new state `s'`:

### Step 1: Compute Inverse Permutations
```python
corner_perm_inv = np.argsort(self.corner_perm)
edge_perm_inv = np.argsort(self.edge_perm)
```

**Why?** The permutation tells us where cubies GO, but we need to know where they CAME FROM.

**Example:** If `corner_perm = [1, 2, 3, 0, ...]`, then:
- The cubie at position 0 came from position 3
- The cubie at position 1 came from position 0
- The cubie at position 2 came from position 1
- The cubie at position 3 came from position 2

So `corner_perm_inv = [3, 0, 1, 2, ...]`

### Step 2: Apply Corner Permutation
```python
new_corner_perm = state.corner_perm[corner_perm_inv]
```

**What this does:** For each position `i` in the new state, find which cubie is there by looking up where it came from.

### Step 3: Apply Corner Orientation
```python
new_corner_orient = (state.corner_orient[corner_perm_inv] + 
                    self.corner_orient_delta) % 3
```

**What this does:** 
1. Get the old orientation of the cubie that moved to position `i`
2. Add the orientation delta
3. Take modulo 3 (since orientations are 0, 1, or 2)

### Step 4: Apply Edge Permutation and Orientation
Same process as corners, but with modulo 2 for orientations.

---

## How to Create a Move Table Entry

Let's walk through creating the **U move** step by step:

### Step 1: Identify Which Cubies Move

**U move rotates the top face clockwise:**
- Top 4 corners: URF(2) → UFL(4) → ULB(5) → UBR(3) → URF(2)
- Top 4 edges: UF(0) → UR(1) → UB(2) → UL(3) → UF(0)

### Step 2: Create Corner Permutation

**Corner positions:**
```
2: URF → moves to position 4 (UFL)
4: UFL → moves to position 5 (ULB)
5: ULB → moves to position 3 (UBR)
3: UBR → moves to position 2 (URF)
0, 1, 6, 7: Don't move
```

**Result:**
```python
corner_perm = [0, 1, 4, 2, 5, 3, 6, 7]
```

### Step 3: Create Corner Orientation Delta

**For U move:** Top corners rotate but stay on the top face, so they don't twist.
- All corners keep the same orientation relative to their faces

**Result:**
```python
corner_orient_delta = [0, 0, 0, 0, 0, 0, 0, 0]
```

### Step 4: Create Edge Permutation

**Edge positions:**
```
0: UF → moves to position 1 (UR)
1: UR → moves to position 2 (UB)
2: UB → moves to position 3 (UL)
3: UL → moves to position 0 (UF)
4-11: Don't move
```

**Result:**
```python
edge_perm = [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11]
```

### Step 5: Create Edge Orientation Delta

**For U move:** Top edges rotate but stay on the top face, so they don't flip.

**Result:**
```python
edge_orient_delta = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

---

## Example: Creating the F Move

The **F move** (Front face clockwise) is more complex because it involves orientation changes.

### Step 1: Identify Moving Cubies

**Corners:**
- URF(2) → DFR(0) → DLF(6) → UFL(4) → URF(2)

**Edges:**
- UF(0) → FR(5) → DF(8) → FL(4) → UF(0)

### Step 2: Corner Permutation

```
2: URF → moves to position 0 (DFR)
0: DFR → moves to position 6 (DLF)
6: DLF → moves to position 4 (UFL)
4: UFL → moves to position 2 (URF)
Others: Don't move
```

**Result:**
```python
corner_perm = [6, 1, 0, 3, 2, 5, 4, 7]
```

### Step 3: Corner Orientation Delta

**When corners move to F face positions, they twist:**
- DFR (position 0): moves to DLF, twists → delta = 1
- URF (position 2): moves to DFR, twists → delta = 1
- UFL (position 4): moves to URF, twists → delta = 1
- DLF (position 6): moves to UFL, twists → delta = 2

**Result:**
```python
corner_orient_delta = [1, 0, 1, 0, 1, 0, 2, 0]
```

### Step 4: Edge Permutation

```
0: UF → moves to position 5 (FR)
5: FR → moves to position 8 (DF)
8: DF → moves to position 4 (FL)
4: FL → moves to position 0 (UF)
```

**Result:**
```python
edge_perm = [5, 1, 2, 3, 0, 8, 6, 7, 4, 9, 10, 11]
```

### Step 5: Edge Orientation Delta

**When edges move to F face positions, they flip:**
- UF (position 0): no flip → delta = 0
- FR (position 5): flips → delta = 1
- DF (position 8): no flip → delta = 0
- FL (position 4): flips → delta = 1

**Result:**
```python
edge_orient_delta = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]
```

---

## Key Insights

1. **Permutation arrays** tell you where cubies GO (destination mapping)
2. **Orientation deltas** tell you how much each cubie twists/flips
3. **Inverse permutations** are needed to find where cubies CAME FROM
4. **U and D moves** don't change orientations (cubies stay on same face)
5. **F, B, L, R moves** change orientations (cubies move to different face orientations)

---

## Verification Tips

To verify a move is correct:

1. **Check permutation cycles:** Make sure all cubies in a cycle are accounted for
2. **Check orientation sums:** 
   - Corner orientations must sum to 0 mod 3
   - Edge orientations must sum to 0 mod 2
3. **Test with solved state:** Apply move to solved state and verify visually
4. **Test inverse:** Apply move then its inverse, should return to original state

---

## Common Patterns

### U/D Moves (No Orientation Changes)
- Only top/bottom layer moves
- Permutations are simple 4-cycles
- All orientation deltas are 0

### F/B Moves (Corner and Edge Orientation Changes)
- Front/back layer moves
- Corners twist (delta = 1 or 2)
- Edges flip (delta = 1)

### L/R Moves (Corner Orientation Changes)
- Left/right layer moves
- Corners twist
- Edges don't flip (they stay on same face orientation)

