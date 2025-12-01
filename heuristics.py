"""
Heuristic functions using pattern databases (Korf-style).
"""

from cube_state import CubeState
from pattern_databases import (
    CornerFullPDB,
    Edge6PDB,
    build_korf_pdbs,
    EDGE_SET_1_POSITIONS,
    EDGE_SET_2_POSITIONS
)


class Heuristic:
    """
    Combined heuristic using Korf-style pattern databases.
    
    Uses:
    - CornerFullPDB: All 8 corners (permutation + orientation)
    - Edge6PDB A: First set of 6 edges
    - Edge6PDB B: Second set of 6 edges (disjoint from A)
    
    Heuristic: h(s) = max(h_corner(s), h_edge6A(s), h_edge6B(s))
    """
    
    def __init__(self, corner_pdb: CornerFullPDB = None,
                 edge6a_pdb: Edge6PDB = None,
                 edge6b_pdb: Edge6PDB = None,
                 cache_dir: str = "pdb_cache"):
        """
        Initialize heuristic with Korf-style pattern databases.
        
        Args:
            corner_pdb: CornerFullPDB instance (built/loaded if None)
            edge6a_pdb: Edge6PDB instance (built/loaded if None)
            edge6b_pdb: Edge6PDB instance (built/loaded if None)
            cache_dir: Directory for caching PDB files (default: "pdb_cache")
        
        If PDBs are None, they will be built/loaded automatically from cache.
        """
        if corner_pdb is None:
            print("Loading/Building Korf-style pattern databases...")
            print("  (Will use cache if available, otherwise will build)")
            print()
            corner_pdb, edge6a_pdb, edge6b_pdb = build_korf_pdbs(cache_dir=cache_dir)
        
        self.corner_pdb = corner_pdb
        self.edge6a_pdb = edge6a_pdb
        self.edge6b_pdb = edge6b_pdb
    
    def h_corner(self, state: CubeState) -> float:
        """Corner full heuristic (permutation + orientation)."""
        index = self.corner_pdb.abstract(state)
        return self.corner_pdb.get(index)
    
    def h_edge6a(self, state: CubeState) -> float:
        """Edge6A heuristic (first set of 6 edges)."""
        index = self.edge6a_pdb.abstract(state)
        return self.edge6a_pdb.get(index)
    
    def h_edge6b(self, state: CubeState) -> float:
        """Edge6B heuristic (second set of 6 edges)."""
        index = self.edge6b_pdb.abstract(state)
        return self.edge6b_pdb.get(index)
    
    def h(self, state: CubeState) -> float:
        """
        Combined heuristic using max combination (Korf's method, always admissible).
        
        Args:
            state: cube state
        
        Returns:
            Heuristic value: max(h_corner, h_edge6A, h_edge6B)
        """
        h_corner = self.h_corner(state)
        h_edge6a = self.h_edge6a(state)
        h_edge6b = self.h_edge6b(state)
        
        return max(h_corner, h_edge6a, h_edge6b)

