"""
Heuristic functions using pattern databases.
"""

from cube_state import CubeState
from pattern_databases import (
    CornerOrientationPDB,
    EdgeOrientationPDB,
    CornerPermutationPDB
)


class Heuristic:
    """Combined heuristic using pattern databases."""
    
    def __init__(self, co_pdb: CornerOrientationPDB = None,
                 eo_pdb: EdgeOrientationPDB = None,
                 cp_pdb: CornerPermutationPDB = None):
        """
        Initialize heuristic with pattern databases.
        
        If PDBs are None, they will be built automatically.
        """
        if co_pdb is None:
            print("Building pattern databases...")
            co_pdb = CornerOrientationPDB()
            co_pdb.build()
            eo_pdb = EdgeOrientationPDB()
            eo_pdb.build()
            cp_pdb = CornerPermutationPDB()
            cp_pdb.build()
        
        self.co_pdb = co_pdb
        self.eo_pdb = eo_pdb
        self.cp_pdb = cp_pdb
    
    def h_co(self, state: CubeState) -> float:
        """Corner orientation heuristic."""
        index = self.co_pdb.abstract(state)
        return self.co_pdb.get(index)
    
    def h_eo(self, state: CubeState) -> float:
        """Edge orientation heuristic."""
        index = self.eo_pdb.abstract(state)
        return self.eo_pdb.get(index)
    
    def h_cp(self, state: CubeState) -> float:
        """Corner permutation heuristic."""
        index = self.cp_pdb.abstract(state)
        return self.cp_pdb.get(index)
    
    def h(self, state: CubeState, method: str = 'max') -> float:
        """
        Combined heuristic.
        
        Args:
            state: cube state
            method: 'max' for max combination (always admissible),
                   'add' for additive combination (may not be admissible)
        
        Returns:
            Heuristic value
        """
        h_co = self.h_co(state)
        h_eo = self.h_eo(state)
        h_cp = self.h_cp(state)
        
        if method == 'max':
            return max(h_co, h_eo, h_cp)
        elif method == 'add':
            return h_co + h_eo + h_cp
        else:
            raise ValueError(f"Unknown method: {method}")

