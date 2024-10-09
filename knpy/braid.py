import numpy as np
import torch
import braidvisualiser as bv
import warnings
from typing import List
from .data_utils import knots_in_braid_notation_dict


class Braid:
    def __init__(self,sigmas: List[int] | str, notation_index: int = 0):
        """
        Init Braid class, sigmas should not contain zero or bigger value than n_strands
        sigmas: Braid notation, e.g. [1,-1,2] or the string name of knot e.g. 4_1 #TODO Above 10 there a and n knots (e. g. 11a,13n)
        notation_index: If sigmas is a name of braid than it is possible that multiple notations are available to the same knot. notation_index says which one to choose from these.
        #TODO 10_136 {{-1;-1;-2;3;-2;1;-2;-2;3;2;2};{-1;2;-1;2;3;-2;-2;-4;3;-4}}? Which one?
        #TODO 11n_8,{{-1;-1;-2;1;-2;-1;3;-2;-2;-4;3;-4};{1;2;-1;2;3;-2;-1;-1;-2;-2;-3;-3;-2}}? Which one?
        """
        if type(sigmas) is str:
            self._braid = np.array(knots_in_braid_notation_dict[sigmas][notation_index])
        else:
            self._braid = np.array(sigmas)
        self._n = np.max(np.abs(self._braid)) + 1
    
    def values(self):
        """
        Returns (self._n,self._braid) values as tuple
        #TODO Does it copies by default?    
        """
        return (self._n,self._braid)
    
    def to_torch(self):
        """
        Returns self._braid represented as torch.tensor 
        #TODO Does it copies by default?
        """
        return torch.from_numpy(self._braid)
    
    def show(self):
        bv.Braid(*([self._n] + list(self._braid))).draw()

    #Action functions from paper https://arxiv.org/pdf/2010.16263

    def shift_left(self,inplace=True):
        """
        Shifts the braid left by one
        inplace: Whether to change the original braid as well.
        """
        left_shifted_braid = np.concatenate((self._braid[1:],self._braid[:1]))
        self._braid = left_shifted_braid
        """
        if (inplace):
            self._braid = left_shifted_braid
        
        return left_shifted_braid
        """

    def shift_right(self):
        """
        Shifts the braid left by one
        inplace: Whether to change the original braid as well.
        """
        right_shifted_braid = np.concatenate((self._braid[-1:],self._braid[:-1]))
        self._braid = right_shifted_braid
    
    def conjugation(self,index):
        """
        Conjugates the braid with sigma indexed by index
        index: int in within the interval [-(n-1),n-1], not equal to zero
        """
        assert index != 0, "Index should not be zero"
        assert abs(index)<self._n, f"Index should be less than {self._n}"
        assert type(index) is int, "Provided index should be integer"

        conjugated_braid = np.concatenate((np.array([index]),self._braid,np.array([-index])))
        self._braid = conjugated_braid

    def braid_relation1_and_shift_right(self):
        """
        Applies braid relation 1 at the first possible position, than shifts that chunk to the right end
        """
        position_left = (1 == np.diff(np.abs(self._braid)))
        position_right = (1 == np.diff(np.abs(self._braid[::-1])))
        
        positions = np.where(position_left[:-1] & position_right[-2::-1])[0] #First common postition
        if (positions.shape[0] == 0):
            warnings.warn( "Operation can not be performed, original braid remained")
            return
        position = positions[0]
        signs = np.ones(3)
        to_replace = self._braid[position:position+3]
        signs[to_replace<0] = -1
        replacement = (np.abs(to_replace) + np.array([1,-1,1])) * signs[::-1]
        braid_relation1_and_shift_right_braid = np.concatenate((self._braid[position+3:],self._braid[:position],replacement))
        self._braid = braid_relation1_and_shift_right_braid

    def braid_relation2_and_shift_right(self, inplace=True):
        """
        Applies braid relation 2 at the first possible position, than shifts that chunk to the right end
        """
        positions = np.where(1<np.abs(np.diff(np.abs(self._braid))))[0]
        if (positions.shape[0] == 0):
            warnings.warn( "Operation can not be performed, original braid remained")
            return
        position = positions[0]
        braid_relation2_and_shift_right_braid = np.concatenate((self._braid[position+2:],self._braid[:position],self._braid[(position+1):(position-1):-1]))
        self._braid = braid_relation2_and_shift_right_braid
    
    #Braid relations
    def braid_relation1(self,index):
        """
        Perform first braid relation.
        index: Where the chunk starts, on which operation can be done
        """
        assert index>=0 and index<(self._braid.shape[0]-2), "Invalid index"
        if (abs(self._braid[index+1]) - abs(self._braid[index])) == 1 and (abs(self._braid[index+1]) - abs(self._braid[index+2])) == 1:
            signs = np.ones(3,)
            signs[self._braid[index:index+3] < 0] = -1
            self._braid[index:index+3] = (self._braid[index:index+3] + np.array([1,-1,1])) * signs[::-1]
        else:
            warnings.warn( "Operation can not be performed, original braid remained")
            return

    def braid_relation2(self,index):
        """
        Perform second braid relation.
        index: Where the chunk starts, on which operation can be done
        """
        assert index>=0 and index<(self._braid.shape[0]-1), "Invalid index"
        if abs(abs(self._braid[index]) - abs(self._braid[index+1]) >= 2):
            self._braid[index], self._braid[index+1] = self._braid[index+1], self._braid[index]
        else:
            warnings.warn( "Operation can not be performed, original braid remained")
            return

    #Markov moves
    def conjugation(self,index:int):
        """
        Performs conjugation move.
        index: Index of the element before cut to be preformed.
        """

        conjugated_braid = np.concatenate((self._braid[index:],self._braid[:index]))
        self._braid = conjugated_braid

    def stabilization(self):
        """
        Performs stabilization move.
        """
        braid_stabilized = np.concatenate((self._braid,np.array([self._n])))
        
        self._braid = braid_stabilized
        self._n = self._n + 1

    def destabilization(self):
        """
        Performs destabilization move.
        """
        if self._braid[-1] == self._n - 1 and (not np.any(self._braid[:-1] == self._n)) :
            braid_destabilized = self._braid[:-1]
            
            self._braid = braid_destabilized
            self._n = self._n - 1
        else:
            warnings.warn( "Operation can not be performed, original braid remained")
