"""
Pattern Database (PDB) construction and heuristics.

Implements Korf-style pattern databases:
- CornerFullPDB: All 8 corners (permutation + orientation) = 8! × 3^7 = 88,179,840 states
- Edge6PDB: Two disjoint sets of 6 edges = C(12,6) × 6! × 2^6 = 42,577,920 states each
"""

import numpy as np
import os
import pickle
from math import comb
from collections import deque
from cube_state import CubeState, solved_state
from moves import ALL_MOVES, MOVE_TABLE, MOVE_INVERSE_TABLE, TEMP_CORNER_PERM, TEMP_CORNER_ORIENT


class PatternDatabase:
    """Base class for pattern databases."""
    
    def __init__(self, size: int):
        self.size = size
        self.pdb = np.full(size, np.inf, dtype=np.float32)
    
    def get(self, index: int) -> float:
        """Get heuristic value for a given abstract state index."""
        if 0 <= index < self.size:
            return self.pdb[index]
        return np.inf
    
    def build(self):
        """Build the pattern database. Override in subclasses."""
        raise NotImplementedError
    
    def save(self, filename: str):
        """
        Save PDB to disk using efficient numpy format.
        
        Args:
            filename: base filename (will create .npy and .meta files)
        """
        data_file = filename + '.npy'
        meta_file = filename + '.meta'
        
        print(f"Saving PDB to {data_file}...")
        np.save(data_file, self.pdb, allow_pickle=False)
        
        # Save metadata (include subclass-specific data)
        metadata = {
            'size': self.size,
            'dtype': str(self.pdb.dtype),
            'version': '1.0',
            'class_name': self.__class__.__name__
        }
        
        # Add subclass-specific metadata
        if hasattr(self, 'tracked_positions'):
            metadata['tracked_positions'] = self.tracked_positions
        if hasattr(self, 'name'):
            metadata['name'] = self.name
        
        with open(meta_file, 'wb') as f:
            pickle.dump(metadata, f)
        
        file_size_mb = os.path.getsize(data_file) / (1024 * 1024)
        print(f"  Saved {file_size_mb:.1f} MB to {data_file}")
    
    @classmethod
    def load(cls, filename: str):
        """
        Load PDB from disk.
        
        Args:
            filename: base filename (will load .npy and .meta files)
        
        Returns:
            PatternDatabase instance with loaded data
        """
        data_file = filename + '.npy'
        meta_file = filename + '.meta'
        
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"PDB file not found: {data_file}")
        
        print(f"Loading PDB from {data_file}...")
        
        # Load metadata
        with open(meta_file, 'rb') as f:
            metadata = pickle.load(f)
        
        # Load data (use memory mapping for large files to save RAM)
        file_size_mb = os.path.getsize(data_file) / (1024 * 1024)
        if file_size_mb > 100:  # Use mmap for files > 100MB
            pdb_data = np.load(data_file, mmap_mode='r')
            print(f"  Loading {file_size_mb:.1f} MB (memory-mapped)")
        else:
            pdb_data = np.load(data_file)
            print(f"  Loaded {file_size_mb:.1f} MB")
        
        # Create instance without calling __init__ (to avoid allocating new array)
        instance = cls.__new__(cls)
        instance.size = metadata['size']
        instance.pdb = pdb_data
        
        # Restore subclass-specific attributes
        if 'tracked_positions' in metadata:
            instance.tracked_positions = metadata['tracked_positions']
        if 'name' in metadata:
            instance.name = metadata['name']
        
        return instance
    
    @classmethod
    def exists(cls, filename: str) -> bool:
        """Check if PDB file exists."""
        return os.path.exists(filename + '.npy') and os.path.exists(filename + '.meta')


class CornerOrientationPDB(PatternDatabase):
    """
    Corner Orientation Pattern Database.
    
    Abstracts state to (o_c(0), ..., o_c(6)) ∈ {0,1,2}^7
    o_c(7) is determined by the constraint: sum ≡ 0 (mod 3)
    """
    
    def __init__(self):
        super().__init__(3**7)  # 2187 states
    
    def abstract(self, state: CubeState) -> int:
        """
        Extract corner orientation pattern and return index.
        
        index = sum_{i=0}^{6} o_c(i) * 3^i
        """
        # Optimized: avoid repeated exponentiation
        index = 0
        power = 1
        for i in range(7):
            index += int(state.corner_orient[i]) * power
            power *= 3
        return index
    
    def build(self):
        """Build PDB using reverse BFS from solved state."""
        print("Building Corner Orientation PDB...")
        
        # Initialize: solved state has index 0 and distance 0
        self.pdb[0] = 0
        
        # BFS queue: (state, distance)
        queue = deque([(solved_state(), 0)])
        visited = set()
        visited.add(0)
        
        depth = 0
        nodes_at_depth = 1
        
        while queue:
            state, dist = queue.popleft()
            nodes_at_depth -= 1
            
            # Apply all moves
            for move in ALL_MOVES:
                next_state = move.apply(state)
                abstract_index = self.abstract(next_state)
                
                # If we haven't seen this abstract state, add it
                if abstract_index not in visited:
                    visited.add(abstract_index)
                    self.pdb[abstract_index] = dist + 1
                    queue.append((next_state, dist + 1))
            
            if nodes_at_depth == 0:
                depth += 1
                nodes_at_depth = len(queue)
                if depth % 2 == 0:
                    print(f"  Depth {depth}: {len(visited)}/{self.size} states explored")
        
        print(f"Corner Orientation PDB built: {len(visited)}/{self.size} states")
        print(f"  Max depth: {depth}")
        print(f"  Coverage: {100 * len(visited) / self.size:.1f}%")


class EdgeOrientationPDB(PatternDatabase):
    """
    Edge Orientation Pattern Database.
    
    Abstracts state to (o_e(0), ..., o_e(10)) ∈ {0,1}^11
    o_e(11) is determined by the constraint: sum ≡ 0 (mod 2)
    """
    
    def __init__(self):
        super().__init__(2**11)  # 2048 states
    
    def abstract(self, state: CubeState) -> int:
        """
        Extract edge orientation pattern and return index.
        
        index = sum_{i=0}^{10} o_e(i) * 2^i
        """
        # Optimized: use bit shifting instead of exponentiation
        index = 0
        for i in range(11):
            if state.edge_orient[i]:
                index |= (1 << i)
        return index
    
    def build(self):
        """Build PDB using reverse BFS from solved state."""
        print("Building Edge Orientation PDB...")
        
        # Initialize: solved state has index 0 and distance 0
        self.pdb[0] = 0
        
        # BFS queue: (state, distance)
        queue = deque([(solved_state(), 0)])
        visited = set()
        visited.add(0)
        
        depth = 0
        nodes_at_depth = 1
        
        while queue:
            state, dist = queue.popleft()
            nodes_at_depth -= 1
            
            # Apply all moves
            for move in ALL_MOVES:
                next_state = move.apply(state)
                abstract_index = self.abstract(next_state)
                
                # If we haven't seen this abstract state, add it
                if abstract_index not in visited:
                    visited.add(abstract_index)
                    self.pdb[abstract_index] = dist + 1
                    queue.append((next_state, dist + 1))
            
            if nodes_at_depth == 0:
                depth += 1
                nodes_at_depth = len(queue)
                if depth % 2 == 0:
                    print(f"  Depth {depth}: {len(visited)}/{self.size} states explored")
        
        print(f"Edge Orientation PDB built: {len(visited)}/{self.size} states")
        print(f"  Max depth: {depth}")
        print(f"  Coverage: {100 * len(visited) / self.size:.1f}%")


class CornerPermutationPDB(PatternDatabase):
    """
    Corner Permutation Pattern Database.
    
    Abstracts state to corner permutation p_c ∈ S_8
    Encoded using factorial number system (Lehmer code)
    """
    
    def __init__(self):
        super().__init__(40320)  # 8! = 40320 states
    
    def abstract(self, state: CubeState) -> int:
        """
        Extract corner permutation and return index using Lehmer code.
        
        The Lehmer code encodes a permutation as a sequence of numbers
        representing how many elements to the right are smaller.
        Optimized: avoid copying array, use direct access.
        """
        perm = state.corner_perm  # No need to copy
        index = 0
        factorial = 1
        
        for i in range(7, 0, -1):
            # Count elements to the right that are smaller
            count = 0
            val_i = perm[i]
            for j in range(i + 1, 8):
                if perm[j] < val_i:
                    count += 1
            index += count * factorial
            factorial *= (8 - i)
        
        return index
    
    def build(self):
        """Build PDB using reverse BFS from solved state."""
        print("Building Corner Permutation PDB...")
        
        # Initialize: solved state has index 0 and distance 0
        self.pdb[0] = 0
        
        # BFS queue: (state, distance)
        queue = deque([(solved_state(), 0)])
        visited = set()
        visited.add(0)
        
        depth = 0
        nodes_at_depth = 1
        
        while queue:
            state, dist = queue.popleft()
            nodes_at_depth -= 1
            
            # Apply all moves
            for move in ALL_MOVES:
                next_state = move.apply(state)
                abstract_index = self.abstract(next_state)
                
                # If we haven't seen this abstract state, add it
                if abstract_index not in visited:
                    visited.add(abstract_index)
                    self.pdb[abstract_index] = dist + 1
                    queue.append((next_state, dist + 1))
            
            if nodes_at_depth == 0:
                depth += 1
                nodes_at_depth = len(queue)
                if depth % 3 == 0:
                    print(f"  Depth {depth}: {len(visited)}/{self.size} states explored")
        
        print(f"Corner Permutation PDB built: {len(visited)}/{self.size} states")
        print(f"  Max depth: {depth}")
        print(f"  Coverage: {100 * len(visited) / self.size:.1f}%")


def build_all_pdbs():
    """Build all pattern databases."""
    co_pdb = CornerOrientationPDB()
    co_pdb.build()
    
    eo_pdb = EdgeOrientationPDB()
    eo_pdb.build()
    
    cp_pdb = CornerPermutationPDB()
    cp_pdb.build()
    
    return co_pdb, eo_pdb, cp_pdb


# ============================================================================
# Korf-style Pattern Databases
# ============================================================================

def lehmer_encode(perm):
    """Encode permutation using Lehmer code (factorial number system)."""
    n = len(perm)
    index = 0
    factorial = 1
    
    # Process from right to left (positions n-1 down to 0)
    for i in range(n - 1, -1, -1):
        count = 0
        val_i = perm[i]
        for j in range(i + 1, n):
            if perm[j] < val_i:
                count += 1
        index += count * factorial
        factorial *= (n - i)
    
    return index


def lehmer_decode(n, index):
    """Decode Lehmer code to permutation."""
    perm = list(range(n))
    result = [0] * n
    factorial = 1
    for i in range(1, n):
        factorial *= i
    
    for i in range(n - 1):
        f = factorial
        factorial //= (n - 1 - i) if (n - 1 - i) > 0 else 1
        digit = index // f
        index %= f
        result[i] = perm.pop(digit)
    
    if perm:
        result[n - 1] = perm[0]
    
    return result


def encode_corner_orient(orient):
    """Encode corner orientation (base-3, 7 digits)."""
    index = 0
    power = 1
    for i in range(7):
        index += orient[i] * power
        power *= 3
    return index


def decode_corner_orient(index):
    """Decode corner orientation from index."""
    orient = [0] * 8
    for i in range(7):
        orient[i] = index % 3
        index //= 3
    # o_c(7) determined by constraint: sum ≡ 0 (mod 3)
    orient[7] = (3 - sum(orient[:7]) % 3) % 3
    return orient


class CornerFullPDB(PatternDatabase):
    """
    Korf-style Full Corner Pattern Database.
    
    Abstracts: All 8 corners (permutation + orientation)
    Ignores: All edges
    
    State count: 8! × 3^7 = 40,320 × 2,187 = 88,179,840
    """
    
    PERM_SIZE = 40320  # 8!
    ORIENT_SIZE = 2187  # 3^7
    
    def __init__(self):
        super().__init__(self.PERM_SIZE * self.ORIENT_SIZE)
    
    def abstract(self, state: CubeState) -> int:
        """
        Extract full corner pattern (permutation + orientation).
        
        Index = perm_index * 2187 + orient_index
        """
        perm_index = lehmer_encode(state.corner_perm)
        orient_index = encode_corner_orient(state.corner_orient)
        return perm_index * self.ORIENT_SIZE + orient_index
    
    def apply_move_to_abstract(self, abstract_index: int, move) -> int:
        """
        Apply a move directly to an abstract index, returning new abstract index.
        Optimized: avoids creating full CubeState objects.
        
        Args:
            abstract_index: current abstract index
            move: Move object to apply
        
        Returns:
            new abstract index after applying move
        """
        # Decode abstract index
        perm_index = abstract_index // self.ORIENT_SIZE
        orient_index = abstract_index % self.ORIENT_SIZE
        
        # Decode to corner perm and orient
        corner_perm = lehmer_decode(8, perm_index)
        corner_orient = decode_corner_orient(orient_index)
        
        # Apply move to corners only (using temp buffers)
        temp_corner_perm = TEMP_CORNER_PERM
        temp_corner_orient = TEMP_CORNER_ORIENT
        
        for i in range(8):
            j = move.corner_perm_inv[i]
            temp_corner_perm[i] = corner_perm[j]
            temp_corner_orient[i] = (corner_orient[j] + move.corner_orient_delta[i]) % 3
        
        # Encode back to abstract index
        new_perm_index = lehmer_encode(temp_corner_perm)
        new_orient_index = encode_corner_orient(temp_corner_orient)
        return new_perm_index * self.ORIENT_SIZE + new_orient_index
    
    def build(self, cache_file: str = None):
        """
        Build PDB using BFS from solved abstract state.
        
        Args:
            cache_file: If provided, save to this file after building.
                       If file exists, load from it instead of building.
        """
        # Check if cached file exists
        if cache_file and self.exists(cache_file):
            print(f"Loading Corner Full PDB from cache: {cache_file}")
            loaded = CornerFullPDB.load(cache_file)
            self.pdb = loaded.pdb
            self.size = loaded.size
            return
        
        print("Building Corner Full PDB (Korf-style)...")
        print(f"  Total states: {self.size:,}")
        
        # Initialize: solved state has index 0 and distance 0
        solved_index = self.abstract(solved_state())
        self.pdb[solved_index] = 0
        
        # BFS queue: (abstract_index, distance)
        queue = deque([(solved_index, 0)])
        # Optimization #4: Use NumPy boolean array instead of Python set (faster lookups)
        visited = np.zeros(self.size, dtype=np.bool_)
        visited[solved_index] = True
        visited_count = 1
        
        depth = 0
        nodes_at_depth = 1
        states_processed = 0
        last_print_count = 0
        
        while queue:
            abstract_index, dist = queue.popleft()
            nodes_at_depth -= 1
            states_processed += 1
            
            # Print progress every 5,000,000 states (Optimization #5: less frequent prints)
            if states_processed - last_print_count >= 5000000:
                print(f"  [PROGRESS] Processed {states_processed:,} states ({visited_count:,} unique, {100*visited_count/self.size:.2f}% coverage)", flush=True)
                last_print_count = states_processed
            
            # Optimization #1: Apply moves directly to abstract indices (no state creation)
            for move in ALL_MOVES:
                next_index = self.apply_move_to_abstract(abstract_index, move)
                
                if not visited[next_index]:
                    visited[next_index] = True
                    visited_count += 1
                    self.pdb[next_index] = dist + 1
                    queue.append((next_index, dist + 1))
            
            if nodes_at_depth == 0:
                depth += 1
                nodes_at_depth = len(queue)
                if depth % 2 == 0:
                    print(f"  Depth {depth}: {visited_count:,}/{self.size:,} states explored ({100*visited_count/self.size:.2f}%)")
        
        print(f"Corner Full PDB built: {visited_count:,}/{self.size:,} states")
        print(f"  Max depth: {depth}")
        print(f"  Coverage: {100 * visited_count / self.size:.2f}%")
        
        # Save to cache if requested
        if cache_file:
            self.save(cache_file)


# Edge sets for Korf-style 6-edge PDBs
# Set 1: {UF, UR, UB, UL, FR, BR} = positions {0, 1, 2, 3, 5, 6}
# Set 2: {DF, DR, DB, DL, FL, BL} = positions {8, 9, 10, 11, 4, 7}
EDGE_SET_1_POSITIONS = [0, 1, 2, 3, 5, 6]  # UF, UR, UB, UL, FR, BR
EDGE_SET_2_POSITIONS = [8, 9, 10, 11, 4, 7]  # DF, DR, DB, DL, FL, BL


# Precomputed binomial coefficient cache for C(12,6) case (most common)
# Cache all binomial coefficients we might need during combination_index calls
_COMB_CACHE = {}

def _get_comb(n, k):
    """Get binomial coefficient with caching for common cases."""
    if n < 0 or k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    # Use cache for smaller values (most common in our use case)
    if n <= 12 and k <= 6:
        key = (n, k)
        if key not in _COMB_CACHE:
            _COMB_CACHE[key] = comb(n, k)
        return _COMB_CACHE[key]
    return comb(n, k)

def combination_index(combination, n, k, start_idx=0):
    """
    Encode a combination of k elements from n as an index.
    combination should be sorted list of k distinct elements from [0..n-1]
    Returns index in range [0, C(n,k)-1]
    
    Optimized version using cached binomial coefficients and avoiding list copies.
    """
    if k == 0:
        return 0
    
    # Use start_idx to avoid creating sublists (optimization for recursive calls)
    first = combination[start_idx]
    index = 0
    
    # Sum C(n-1-j, k-1) for j < first (using cached comb)
    for j in range(first):
        index += _get_comb(n - 1 - j, k - 1)
    
    # Add index of remaining combination (recursive, but pass start_idx instead of creating list)
    if k > 1:
        # Adjust combination values: for remaining[i], original value is combination[start_idx+1+i]
        # In the recursive call, we treat it as if it's starting from 0, so we subtract (first+1)
        # But we can avoid creating a new list by adjusting the values on-the-fly
        # Actually, we need to pass the adjusted values... let's just create the small list
        # (for k=6, this creates at most 5 elements, which is acceptable)
        remaining_len = k - 1
        remaining = [0] * remaining_len
        for i in range(remaining_len):
            remaining[i] = combination[start_idx + 1 + i] - first - 1
        index += combination_index(remaining, n - first - 1, k - 1)
    
    return index


# Reusable temporary buffers for encode_edge6_pattern (avoid allocations)
_TEMP_TRACKED_CUBIES = [0] * 6
_TEMP_SORTED_CUBIES = [0] * 6
_TEMP_PERM_IN_SORTED = [0] * 6

def encode_edge6_pattern(state, tracked_positions):
    """
    Encode 6-edge pattern.
    
    Returns: (which_6_edges_index, perm_index, orient_index)
    where:
    - which_6_edges_index: which 6 edge cubies are in tracked positions (0 to C(12,6)-1)
    - perm_index: permutation of those 6 edges (0 to 6!-1)
    - orient_index: orientation bits (0 to 2^6-1)
    
    Optimized version using reusable temp buffers to avoid allocations.
    """
    # Get the 6 edge cubies in tracked positions (reuse temp buffer)
    for i, pos in enumerate(tracked_positions):
        _TEMP_TRACKED_CUBIES[i] = state.edge_perm[pos]
    
    # Sort to get canonical "which edges" representation (in-place sort of copy)
    _TEMP_SORTED_CUBIES[:] = _TEMP_TRACKED_CUBIES[:]
    _TEMP_SORTED_CUBIES.sort()
    
    # Encode which 6 edges using combination index
    which_edges_index = combination_index(_TEMP_SORTED_CUBIES, 12, 6)
    
    # Map tracked_cubies to indices in sorted list for permutation encoding
    # Since cubies are distinct, we can build a simple mapping array
    # sorted_cubies[j] gives the cubie at sorted index j
    # We need: for each tracked_cubie[i], find j such that sorted_cubies[j] == tracked_cubie[i]
    for i in range(6):
        cubie = _TEMP_TRACKED_CUBIES[i]
        # Linear search (only 6 elements, very fast)
        for j in range(6):
            if _TEMP_SORTED_CUBIES[j] == cubie:
                _TEMP_PERM_IN_SORTED[i] = j
                break
    
    perm_index = lehmer_encode(_TEMP_PERM_IN_SORTED)
    
    # Encode orientations (6 bits) - compute directly without list
    orient_index = 0
    for i, pos in enumerate(tracked_positions):
        if state.edge_orient[pos]:
            orient_index |= (1 << i)
    
    return which_edges_index, perm_index, orient_index


class Edge6PDB(PatternDatabase):
    """
    Korf-style 6-Edge Pattern Database.
    
    Tracks a specific set of 6 edge positions.
    Abstracts: positions + permutation + orientation of those 6 edges
    Ignores: other 6 edges, all corners
    
    State count: C(12,6) × 6! × 2^6 = 924 × 720 × 64 = 42,577,920
    """
    
    # Approximate sizes (actual encoding may vary)
    WHICH_EDGES_SIZE = 924  # C(12,6)
    PERM_SIZE = 720  # 6!
    ORIENT_SIZE = 64  # 2^6
    
    def __init__(self, tracked_positions, name="Edge6", load_from_cache: bool = False):
        """
        Initialize 6-edge PDB.
        
        Args:
            tracked_positions: list of 6 edge position indices to track
            name: name for this PDB (for logging)
            load_from_cache: If True, don't allocate array (for loading from disk)
        """
        # For now, use approximate size - will refine encoding later
        estimated_size = self.WHICH_EDGES_SIZE * self.PERM_SIZE * self.ORIENT_SIZE
        if not load_from_cache:
            super().__init__(estimated_size)
        self.tracked_positions = tracked_positions
        self.name = name
    
    def abstract(self, state: CubeState) -> int:
        """Extract 6-edge pattern and return index."""
        which_edges, perm_idx, orient_idx = encode_edge6_pattern(state, self.tracked_positions)
        # Simple encoding (may need refinement)
        index = which_edges * self.PERM_SIZE * self.ORIENT_SIZE
        index += perm_idx * self.ORIENT_SIZE
        index += orient_idx
        return index
    
    def build(self, cache_file: str = None):
        """
        Build PDB using BFS from solved abstract state.
        
        Args:
            cache_file: If provided, save to this file after building.
                       If file exists, load from it instead of building.
        """
        # Check if cached file exists
        if cache_file and Edge6PDB.exists(cache_file):
            print(f"Loading {self.name} PDB from cache: {cache_file}")
            loaded = Edge6PDB.load(cache_file)
            self.pdb = loaded.pdb
            self.size = loaded.size
            self.tracked_positions = loaded.tracked_positions
            self.name = loaded.name
            return
        
        print(f"Building {self.name} PDB (Korf-style)...")
        print(f"  Tracked positions: {self.tracked_positions}")
        print(f"  Estimated states: {self.size:,}")
        
        # Initialize: solved state
        solved_state_obj = solved_state()
        solved_index = self.abstract(solved_state_obj)
        if solved_index < self.size:
            self.pdb[solved_index] = 0
        
        # BFS queue: store states (decoding Edge6PDB abstract index is complex)
        queue = deque([(solved_state_obj, 0)])
        # Optimization #4: Use NumPy boolean array instead of Python set
        visited = np.zeros(self.size, dtype=np.bool_)
        if solved_index < self.size:
            visited[solved_index] = True
        visited_count = 1
        
        depth = 0
        nodes_at_depth = 1
        states_processed = 0
        last_print_count = 0
        
        # Optimization #2: Reusable working state for in-place operations
        working_state = CubeState()
        
        while queue:
            state, dist = queue.popleft()
            nodes_at_depth -= 1
            states_processed += 1
            
            # Print progress every 5,000,000 states (Optimization #5: less frequent prints)
            if states_processed - last_print_count >= 5000000:
                print(f"  [PROGRESS] Processed {states_processed:,} states ({visited_count:,} unique, {100*visited_count/self.size:.2f}% coverage)", flush=True)
                last_print_count = states_processed
            
            # Optimization #2: Use in-place operations - copy state once, apply moves in-place
            # Copy state to working_state
            working_state.corner_perm = state.corner_perm[:]
            working_state.corner_orient = state.corner_orient[:]
            working_state.edge_perm = state.edge_perm[:]
            working_state.edge_orient = state.edge_orient[:]
            
            # Apply all moves in-place
            for move in ALL_MOVES:
                move.apply_in_place(working_state)
                abstract_index = self.abstract(working_state)
                
                if abstract_index < self.size and not visited[abstract_index]:
                    visited[abstract_index] = True
                    visited_count += 1
                    self.pdb[abstract_index] = dist + 1
                    # Only copy when adding to queue
                    queue.append((working_state.copy(), dist + 1))
                
                # Undo move to reuse working_state
                inverse_move = MOVE_INVERSE_TABLE[move]
                inverse_move.apply_in_place(working_state)
            
            if nodes_at_depth == 0:
                depth += 1
                nodes_at_depth = len(queue)
                if depth % 2 == 0:
                    print(f"  Depth {depth}: {visited_count:,} states explored")
        
        print(f"{self.name} PDB built: {visited_count:,} states")
        print(f"  Max depth: {depth}")
            
            # Reconstruct state from abstract index (needed for move application)
            # For Edge6PDB, decoding is complex, so we'll reconstruct by applying inverse moves
            # Actually, we can't easily decode Edge6PDB abstract index back to state
            # So we'll use a different approach: store state in queue but use in-place operations
            
            # Actually, let me keep it simpler: store states but use in-place operations
            # This is still a significant optimization
            
            # For now, let's use a hybrid: store abstract indices and reconstruct state when needed
            # But this requires decoding which is complex for Edge6PDB...
            
            # Let's use a simpler optimization: store states but use in-place operations
            # We'll need to change the queue structure
            
            # Actually, I realize the current structure stores states. Let me optimize by:
            # 1. Using in-place operations
            # 2. NumPy visited array
            # 3. Less frequent prints
            
            # Since Edge6PDB encoding/decoding is complex, let's keep states in queue
            # but optimize with in-place operations and NumPy visited
            
            # Wait, I need to rethink this. The queue currently stores states.
            # Let me check the actual structure again...
            
            # Actually, I see the issue - the current code stores states in queue.
            # For Edge6PDB, decoding is too complex, so let's optimize differently:
            # - Use NumPy visited array
            # - Use in-place operations with a reusable working state
            # - Store abstract indices in queue and reconstruct state only when needed
            
            # But reconstructing from abstract index is complex for Edge6PDB.
            # So let's use a different approach: store (abstract_index, state) pairs
            # but use in-place operations to avoid creating new states for moves
            
            # Actually, the simplest optimization: keep current structure but:
            # 1. Use NumPy visited array
            # 2. Use in-place operations (copy state once, apply moves in-place)
            
            # Let me implement a simpler version that still gives good speedup
        
        # Save to cache if requested
        if cache_file:
            self.save(cache_file)


def build_korf_pdbs(cache_dir: str = "pdb_cache"):
    """
    Build Korf-style pattern databases.
    
    Args:
        cache_dir: Directory to store/load cached PDB files
    
    Returns:
        Tuple of (corner_pdb, edge6a_pdb, edge6b_pdb)
    """
    # Create cache directory if it doesn't exist
    if cache_dir and not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    print("Building/loading Korf-style pattern databases...")
    print()
    
    # Build or load corner PDB
    corner_cache = os.path.join(cache_dir, "corner_full") if cache_dir else None
    corner_pdb = CornerFullPDB()
    corner_pdb.build(cache_file=corner_cache)
    print()
    
    # Build or load edge6a PDB
    edge6a_cache = os.path.join(cache_dir, "edge6a") if cache_dir else None
    edge6a_pdb = Edge6PDB(EDGE_SET_1_POSITIONS, "Edge6A")
    edge6a_pdb.build(cache_file=edge6a_cache)
    print()
    
    # Build or load edge6b PDB
    edge6b_cache = os.path.join(cache_dir, "edge6b") if cache_dir else None
    edge6b_pdb = Edge6PDB(EDGE_SET_2_POSITIONS, "Edge6B")
    edge6b_pdb.build(cache_file=edge6b_cache)
    
    return corner_pdb, edge6a_pdb, edge6b_pdb

