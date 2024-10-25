import numpy as np
import torch
import braidvisualiser as bv
import warnings
from functools import partial
from typing import List
from .data_utils import knots_in_braid_notation_dict
from .exceptions import IllegalTransformationException, InvalidBraidException, IndexOutOfRangeException


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
            if not all(isinstance(x, int) for x in sigmas):
                raise InvalidBraidException
            self._braid = np.array(sigmas)
        
        if np.any(self._braid == 0):
            raise InvalidBraidException
        
        if(self._braid.shape[0] == 0):
            self._n = 1
        else:
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
        left_shifted_braid = self.shift_left_with_amount(amount=1,inplace=False)
        if inplace:
            self._braid = left_shifted_braid
        else:
            return left_shifted_braid

    def shift_right(self,inplace=True):
        """
        Shifts the braid left by one
        inplace: Whether to change the original braid as well.
        """
        right_shifted_braid = self.shift_right_with_amount(amount=1,inplace=False)
        if inplace:
            self._braid = right_shifted_braid
        else:
            return right_shifted_braid
        
    def shift_left_with_amount(self,amount,inplace=True):
        """
        Shifts the braid left by one
        inplace: Whether to change the original braid as well.
        """
        left_shifted_braid = np.concatenate((self._braid[amount:],self._braid[:amount]))
        if inplace:
            self._braid = left_shifted_braid
        else:
            return left_shifted_braid
    
    def shift_right_with_amount(self,amount,inplace=True):
        """
        Shifts the braid left by one
        inplace: Whether to change the original braid as well.
        """
        right_shifted_braid = np.concatenate((self._braid[-amount:],self._braid[:-amount]))
        if inplace:
            self._braid = right_shifted_braid
        else:
            return right_shifted_braid

    def braid_relation2_and_shift_right(self, inplace=True):
        """
        Applies braid relation 2 at the first possible position, than shifts that chunk to the right end
        """

        if self.is_braid_relation_2_and_shift_right_performable():
            indices = self.braid_relation2_performable_indices()
            index = indices[0]
            self.braid_relation2(index)
            transformed_braid = self.shift_right_with_amount(self._braid.shape[0] - index - 2, inplace=False)
            
            if(inplace):
                self._braid = transformed_braid
            else:
                self.braid_relation2(index)
                return transformed_braid
        else:
            raise IllegalTransformationException

        """
        positions = np.where(1<np.abs(np.diff(np.abs(self._braid))))[0]
        if (positions.shape[0] == 0):
            warnings.warn( "Operation can not be performed, original braid remained")
            return
        position = positions[0]
        braid_relation2_and_shift_right_braid = np.concatenate((self._braid[position+2:],self._braid[:position],self._braid[(position+1):(position-1):-1]))
        self._braid = braid_relation2_and_shift_right_braid
        """
    
    #Braid relations
    def braid_relation1(self,index,inplace=True):
        """
        Perform first braid relation. Maps between chunks `[±a, ±(a + 1), ±a] ↔ [±(a + 1), ±a, ±(a + 1)]`, `[∓a, ±(a + 1), ±a] ↔ [±(a + 1), ±a, ∓(a + 1)]` and `[±a, ±(a + 1), ∓a] ↔ [∓(a + 1), ±a, ±(a + 1)]` (where all `±` have the same sign and all `∓` have the opposite). `[±a, ∓(a + 1), ±a] ↔ [±(a + 1), ∓a, ±(a + 1)]` is NOT allowed.
        index: Where the chunk starts, on which operation can be done

        *** DUE TO LEGACY REASONS, INPLACE=TRUE WILL RETURN ONLY THE _BRAID MEMBER, A NUMPY ARRAY!!! ***
        """
        #TODO Error
        #TODO Opposite direction should work as well
        #assert index>=0 and index<(self._braid.shape[0]-2), "Invalid index"
        if  self.is_braid_relation1_performable(index):
            signs = np.ones(3,)
            signs[self._braid[index:index+3] < 0] = -1
            transformed_braid = self._braid 
            transformed_braid[index:index+3] = (abs(self._braid)[[index+1,index,index+1]]) * signs[::-1]
            if inplace:
                self._braid = transformed_braid
            else:
                return transformed_braid
        else:
            raise IllegalTransformationException

    def braid_relation2(self,index,inplace=True):
        """
        Perform second braid relation.
        index: Where the chunk starts, on which operation can be done
        """
        #assert index>=0 and index<(self._braid.shape[0]-1), "Invalid index"
        if self.is_braid_relation2_performable(index):
            transformed_braid = self._braid
            transformed_braid[index], transformed_braid[index+1] = transformed_braid[index+1], transformed_braid[index]
            if inplace:
                self._braid = transformed_braid
            else:
                return transformed_braid
        else:
            raise IllegalTransformationException

    #Markov moves
    def conjugation(self,index,inplace = True):
        """
        Conjugates the braid with sigma indexed by index
        index: int in within the interval [-(n-1),n-1], not equal to zero
        """
        """
        assert index != 0, "Index should not be zero"
        assert abs(index)<self._n, f"Index should be less than {self._n}"
        assert type(index) is int, "Provided index should be integer"
        """
        if self.is_conjugation_performable(index):
            conjugated_braid = np.concatenate((np.array([index]),self._braid,np.array([-index])))
            if(inplace):
                self._braid = conjugated_braid
            else:
                return conjugated_braid
        else:
            raise IllegalTransformationException

    def stabilization(self,inverse = False,inplace = True):
        """
        Performs stabilization move.
        """
        if inverse:
            braid_stabilized = np.concatenate((self._braid,np.array([-self._n])))
        else:
            braid_stabilized = np.concatenate((self._braid,np.array([self._n])))
        if inplace:
            self._braid = braid_stabilized
            self._n = self._n + 1
        else:
            return braid_stabilized

    def destabilization(self,inplace = True):
        """
        Performs destabilization move.
        """
        if self.is_destabilization_performable() :
            braid_destabilized = self._braid[:-1]
            if inplace:
                self._braid = braid_destabilized
                self._n = self._n - 1
            else:
                return braid_destabilized

        else:
            raise IllegalTransformationException
    
    def remove_sigma_inverse_pair(self,index,inplace=True):
        """
        Remove consequtive inverse on a given place
        """
        if self.is_remove_sigma_inverse_pair_performable(index):
            transformed_braid = self._braid
            mask = np.ones(self._braid.shape,dtype="bool")
            mask[index] = False
            mask[(index+1)%self._braid.shape[0]] = False
            transformed_braid = transformed_braid[mask]

            if inplace:
                self._braid = transformed_braid
                if(self._braid.shape[0] == 0):
                    self._n = 1
                else:
                    self._n = np.max(np.abs(self._braid)) + 1
            else:
                return transformed_braid
        else:
            raise IllegalTransformationException


    #Chech whether a move is performable or not
    def is_braid_relation1_performable(self,index):
        """
        Check if braid relation 1 is performable at the index. See documentation of `braid_relation1` for details.
        """
        if index >= 0:
            index -= self._braid.shape[0]
        return self._braid.shape[0] != 0 and abs(self._braid[index]) == abs(self._braid[index+2]) and abs(abs(self._braid[index+1]) - abs(self._braid[index])) == 1 and not (np.sign(self._braid[index+1]) != np.sign(self._braid[index]) and np.sign(self._braid[index+1]) != np.sign(self._braid[index+2]))
    
    def braid_relation1_performable_indices(self):
        """
        Returns array of indices where braid relation 1 is performable. See documentation of member function `braid_relation1` for details.
        """
        positions = np.array([])
        for index in range(0,n):
            if is_braid_relation1_performable(self,index):
                positions.append(index)
        return positions

    def is_braid_relation2_performable(self,index):
        return self._braid.shape[0] != 0 and  abs(abs(self._braid[index]) - abs(self._braid[index+1])) >= 2
    
    def braid_relation2_performable_indices(self):
        positions = np.where(1<np.abs(np.diff(np.abs(self._braid))))[0]
        return positions
    
    def is_braid_relation_2_and_shift_right_performable(self):
        return self.braid_relation2_performable_indices().shape[0] != 0

    def is_conjugation_performable(self,index):
        return index != 0 and self._n>abs(index)
    
    def is_destabilization_performable(self):
        return self._braid.shape[0] != 0 and abs(self._braid[-1]) == self._n - 1 and (not np.any(abs(self._braid[:-1]) == self._n - 1))
    
    def is_remove_sigma_inverse_pair_performable(self,index):
        return self._braid.shape[0] != 0 and self._braid[index] + self._braid[(index+1)%self._braid.shape[0]] == 0
    
    def remove_sigma_inverse_pair_performable_indices(self):
        original_braid = self._braid
        shifted_braid = self.shift_left(inplace = False)

        indices = np.where((original_braid + shifted_braid) == 0)[0]

        return indices
    
    def performable_moves(self) -> bool:
        """
        Checks if a move is performable.
        move: The name of the move to check, e.g., "shift_left", "braid_relation1", etc.
        index: Optional index parameter required for some moves.
        Returns: True if the move is performable, otherwise False.
        """
        performable_moves = [self.shift_left,self.shift_right,self.stabilization,partial(self.stabilization,inverse=True)] #Always performable

        if self.is_destabilization_performable():
            performable_moves.append(self.destabilization)
        
        conjugation_indices = list(range(-self._n+1,0)) + list(range(1,self._n))
        conjugation_performable_moves = [partial(self.conjugation,index=i) for i in conjugation_indices]

        performable_moves = performable_moves + conjugation_performable_moves

        braid_relation1_indices = self.braid_relation1_performable_indices()
        braid_relation1_performable_moves = [partial(self.braid_relation1,index=i) for i in braid_relation1_indices]

        performable_moves = performable_moves + braid_relation1_performable_moves

        braid_relation2_indices = self.braid_relation2_performable_indices()
        braid_relation2_performable_moves = [partial(self.braid_relation2,index=i) for i in braid_relation2_indices]

        performable_moves = performable_moves + braid_relation2_performable_moves

        braid_remove_sigma_and_inverse = self.remove_sigma_inverse_pair_performable_indices()
        braid_remove_sigma_and_inverse_moves = [partial(self.remove_sigma_inverse_pair,index=i) for i in braid_remove_sigma_and_inverse]

        performable_moves = performable_moves + braid_remove_sigma_and_inverse_moves

        return performable_moves

