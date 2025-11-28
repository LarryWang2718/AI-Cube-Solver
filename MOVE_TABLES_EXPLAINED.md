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
corner_perm = [1, 2, 3, 0, 4, 5, 6, 7]
```

This means:
- Position 0 → Position 1 (corner at URF moves to UFL)
- Position 1 → Position 2 (corner at UFL moves to ULB)
- Position 2 → Position 3 (corner at ULB moves to UBR)
- Position 3 → Position 0 (corner at UBR moves to URF)
- Positions 4-7 stay the same (bottom corners don't move)

**Corner positions (0-7):**
```
0: URF (Up-Right-Front)
1: UFL (Up-Front-Left)
2: ULB (Up-Left-Back)
3: UBR (Up-Back-Right)
4: DFR (Down-Front-Right)
5: DLF (Down-Left-Front)
6: DBL (Down-Back-Left)
7: DRB (Down-Right-Back)
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
edge_perm = [1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11]
```

This means:
- Position 0 → Position 1 (edge UR moves to UF)
- Position 1 → Position 2 (edge UF moves to UL)
- Position 2 → Position 3 (edge UL moves to UB)
- Position 3 → Position 0 (edge UB moves to UR)
- Positions 4-11 stay the same (middle and bottom edges don't move)

**Edge positions (0-11):**
```
0: UR (Up-Right)
1: UF (Up-Front)
2: UL (Up-Left)
3: UB (Up-Back)
4: DR (Down-Right)
5: DF (Down-Front)
6: DL (Down-Left)
7: DB (Down-Back)
8: FR (Front-Right)
9: FL (Front-Left)
10: BL (Back-Left)
11: BR (Back-Right)
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
- Top 4 corners: URF → UFL → ULB → UBR → URF
- Top 4 edges: UR → UF → UL → UB → UR

### Step 2: Create Corner Permutation

**Corner positions:**
```
0: URF → moves to position 1 (UFL)
1: UFL → moves to position 2 (ULB)
2: ULB → moves to position 3 (UBR)
3: UBR → moves to position 0 (URF)
4-7: Don't move
```

**Result:**
```python
corner_perm = [1, 2, 3, 0, 4, 5, 6, 7]
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
0: UR → moves to position 1 (UF)
1: UF → moves to position 2 (UL)
2: UL → moves to position 3 (UB)
3: UB → moves to position 0 (UR)
4-11: Don't move
```

**Result:**
```python
edge_perm = [1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11]
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
- URF → UFL → DLF → DFR → URF

**Edges:**
- UF → FL → DF → FR → UF

### Step 2: Corner Permutation

```
0: URF → moves to position 1 (UFL)
1: UFL → moves to position 5 (DLF)
5: DLF → moves to position 4 (DFR)
4: DFR → moves to position 0 (URF)
Others: Don't move
```

**Result:**
```python
corner_perm = [1, 5, 2, 3, 0, 4, 6, 7]
# Wait, that's not right! Let me think...

# Actually, we need to think about where each POSITION gets its cubie FROM:
# Position 0 (URF) gets cubie from position 4 (DFR)
# Position 1 (UFL) gets cubie from position 0 (URF)
# Position 4 (DFR) gets cubie from position 5 (DLF)
# Position 5 (DLF) gets cubie from position 1 (UFL)

corner_perm = [1, 5, 2, 3, 0, 4, 6, 7]
```

### Step 3: Corner Orientation Delta

**When corners move to F face positions, they twist:**
- URF (position 0): moves to UFL, twists clockwise → delta = 1
- UFL (position 1): moves to DLF, twists counterclockwise → delta = 2
- DFR (position 4): moves to URF, twists counterclockwise → delta = 2
- DLF (position 5): moves to DFR, twists clockwise → delta = 1

**Result:**
```python
corner_orient_delta = [1, 2, 0, 0, 2, 1, 0, 0]
```

### Step 4: Edge Permutation

```
1: UF → moves to position 9 (FL)
9: FL → moves to position 5 (DF)
5: DF → moves to position 8 (FR)
8: FR → moves to position 1 (UF)
```

**Result:**
```python
edge_perm = [0, 9, 2, 3, 4, 8, 6, 7, 5, 1, 10, 11]
```

### Step 5: Edge Orientation Delta

**When edges move to F face positions, they flip:**
- UF (position 1): flips → delta = 1
- DF (position 5): flips → delta = 1
- FR (position 8): flips → delta = 1
- FL (position 9): flips → delta = 1

**Result:**
```python
edge_orient_delta = [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0]
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

