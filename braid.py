import numpy as np
import braidvisualiser as bv
import warnings
from typing import List


class Braid:
    def __init__(self,n_strands: int, sigmas: List[int]):
        """
        Init Braid class, sigmas should not contain zero or bigger value than n_strands
        n_strands: Number of strands int the braid
        sigmas: Braid notation, e.g. [1,-1,2]
        """
        self._n = n_strands
        self._braid = np.array(sigmas)
        assert not np.any(abs(self._braid) > self._n), "sigmas should be less than n_strands"
    
    def shift_left(self,inplace=True):
        """
        Shifts the braid left by one
        inplace: Whether to change the original braid as well.
        """
        left_shifted_braid = np.concatenate((self._braid[1:],self._braid[:1]))
        if (inplace):
            self._braid = left_shifted_braid
        
        return left_shifted_braid
    
    def shift_right(self,inplace=True):
        """
        Shifts the braid left by one
        inplace: Whether to change the original braid as well.
        """
        right_shifted_braid = np.concatenate((self._braid[-1:],self._braid[:-1]))
        if (inplace):
            self._braid = right_shifted_braid

        return right_shifted_braid
    
    def conjugation(self,index,inplace=True):
        """
        Conjugates the braid with sigma indexed by index
        index: int in within the interval [-(n-1),n-1], not equal to zero
        """
        assert index != 0, "Index should not be zero"
        assert abs(index)<self._n, f"Index should be less than {self._n}"
        assert type(index) is int, "Provided index should be integer"

        conjugated_braid = np.concatenate((np.array([index]),self._braid,np.array([-index])))
        if (inplace):
            self._braid = conjugated_braid
        return conjugated_braid
    
    def braid_relation1_and_shift_right(self,inplace=True):
        """
        Applies braid relation 1 at the first possible position, than shifts that chunk to the right end
        """
        position_left = (1 == np.diff(np.abs(self._braid)))
        position_right = (1 == np.diff(np.abs(self._braid[::-1])))
        
        positions = np.where(position_left[:-1] & position_right[-2::-1])[0] #First common postition
        if (positions.shape[0] == 0):
            warnings.warn( "Operation can not be performed, original braid returned")
            return self._braid
        position = positions[0]
        signs = np.ones(3)
        to_replace = self._braid[position:position+3]
        signs[to_replace<0] = -1
        replacement = (np.abs(to_replace) + np.array([1,-1,1])) * signs[::-1]
        braid_relation1_and_shift_right_braid = np.concatenate((self._braid[position+3:],self._braid[:position],replacement))

        if(inplace):
            self._braid = braid_relation1_and_shift_right_braid
        return braid_relation1_and_shift_right_braid
    
    def braid_relation2_and_shift_right(self, inplace=True):
        """
        Applies braid relation 2 at the first possible position, than shifts that chunk to the right end
        """
        positions = np.where(1<np.abs(np.diff(np.abs(self._braid))))[0]
        if (positions.shape[0] == 0):
            warnings.warn( "Operation can not be performed, original braid returned")
            return self._braid
        position = positions[0]
        braid_relation2_and_shift_right_braid = np.concatenate((self._braid[position+2:],self._braid[:position],self._braid[(position+1):(position-1):-1]))
        if(inplace):
            self._braid = braid_relation2_and_shift_right_braid

        return braid_relation2_and_shift_right_braid
                
    