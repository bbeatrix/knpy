from typing import Callable
import numpy as np
import torch
import braidvisualiser as bv
import warnings
from functools import partial
from .data_utils import knots_in_braid_notation_dict
from .exceptions import IllegalTransformationException, InvalidBraidException, IndexOutOfRangeException

type BraidNotation = np.ndarray
type BraidTransformation = Callable[[], 'Braid']

class Braid:
    def __init__(self,sigmas: np.ndarray | list[int] | str, notation_index: int = 0, copy_sigmas: bool = True):
        """
        Init Braid class, sigmas should not contain zero or bigger value than n_strands
        sigmas: Braid notation, e.g. [1,-1,2] or the string name of knot e.g. 4_1 #TODO Above 10 there a and n knots (e. g. 11a,13n)
        notation_index: If sigmas is a name of braid than it is possible that multiple notations are available to the same knot. notation_index says which one to choose from these.
        #TODO 10_136 {{-1;-1;-2;3;-2;1;-2;-2;3;2;2};{-1;2;-1;2;3;-2;-2;-4;3;-4}}? Which one?
        #TODO 11n_8,{{-1;-1;-2;1;-2;-1;3;-2;-2;-4;3;-4};{1;2;-1;2;3;-2;-1;-1;-2;-2;-3;-3;-2}}? Which one?
        """
        self._braid: BraidNotation
        if isinstance(sigmas, str):
            self._braid = np.array(knots_in_braid_notation_dict[sigmas][notation_index])
        elif isinstance(sigmas, np.ndarray):
            if copy_sigmas:
                self._braid = sigmas.copy()
            else:
                self._braid = sigmas
        else:
            if not all(isinstance(x, (int, np.integer)) for x in sigmas):
                raise InvalidBraidException
            self._braid = np.array(sigmas)
        
        if np.any(self._braid == 0):
            raise InvalidBraidException
        
        if(len(self) == 0):
            self._n = 1
        else:
            self._n = np.max(np.abs(self._braid)) + 1
    
    def values(self) -> tuple[int, BraidNotation]:
        """
        Returns (self._n,self._braid) values as tuple
        """
        return (self._n,self._braid.copy())

    def notation(self, copy = True) -> BraidNotation:
        """
        Returns numpy array of sigmas
        """
        if copy:
            return self._braid.copy()
        else:
            return self._braid

    def strand_count(self) -> int:
        return self._n
    
    def to_torch(self) -> torch.Tensor:
        """
        Returns self._braid represented as torch.tensor 
        #TODO Does it copies by default?
        """
        return torch.from_numpy(self._braid)
    
    def show(self) -> None:
        bv.Braid(*([self._n] + list(self._braid))).draw()

    #Action functions from paper https://arxiv.org/pdf/2010.16263
        
    def shift_left(self, amount: int=1) -> 'Braid':
        """
        Shifts the crossings of the braid left. Numbering the original crossings as `[0, 1, 2, ..., n - 1]` it transforms it to `[amount, amount + 1, amount + 2, ..., n - 2, n - 1, 0, 1, 2, ..., amount - 1]`.
        amount: in the range (-n, n) where n is the number of crossings in the braid (so n = len(braid))
        """

        if amount >= len(self._braid) or amount <= -len(self._braid):
            raise IllegalTransformationException(f"amount = {amount} not in range ({-len(self._braid)}, {len(self._braid)})")

        left_shifted_braid = np.concatenate((self._braid[amount:],self._braid[:amount]))
        return Braid(left_shifted_braid, copy_sigmas=False)
    
    def shift_right(self, amount: int=1) -> 'Braid':
        """
        Shifts the crossings of the braid right. Same as shifting left by the negative amount.
        amount: in the range (-n, n) where n is the number of crossings in the braid (so n = len(braid))
        """

        if amount >= len(self._braid) or amount <= -len(self._braid):
            raise IllegalTransformationException(f"amount = {amount} not in range ({-len(self._braid)}, {len(self._braid)})")

        return self.shift_left(-amount)

    #Braid relations
    def braid_relation1(self,index: int) -> 'Braid':
        """
        Perform first braid relation. Maps between chunks `[±a, ±(a + 1), ±a] ↔ [±(a + 1), ±a, ±(a + 1)]`, `[∓a, ±(a + 1), ±a] ↔ [±(a + 1), ±a, ∓(a + 1)]` and `[±a, ±(a + 1), ∓a] ↔ [∓(a + 1), ±a, ±(a + 1)]` (where all `±` have the same sign and all `∓` have the opposite). `[±a, ∓(a + 1), ±a] ↔ [±(a + 1), ∓a, ±(a + 1)]` is NOT allowed.

        The elements of the chuck must be distict, so the braid must consist of at least 3 crossings. The braid is assumed to be circular, the chunk may cross the end of the array (so some elements from the end, then some elements from the beginning).

        index: Where the chunk starts, on which operation can be done; in the range [-n, n) where n is the number of crossings in the braid (so n = len(braid))
        """
        if self.is_braid_relation1_performable(index):
            signs = np.ones(3,)
            if index > 0:
                index -= len(self._braid)
            signs[self._braid[[index, index + 1, index + 2]] < 0] = -1
            transformed_braid = self._braid.copy()
            transformed_braid[[index, index + 1, index + 2]] = (abs(self._braid)[[index+1,index,index+1]]) * signs[::-1]

            return Braid(transformed_braid, copy_sigmas=False)
        else:
            raise IllegalTransformationException

    def braid_relation2(self,index: int) -> 'Braid':
        """
        Perform second braid relation. Maps between the chunks `[i, j] ↔ [j, i]` if `abs(abs(i) - abs(j)) >= 2`.

        The elements of the chuck must be distict, so the braid must consist of at least 2 crossings. The braid is assumed to be circular, the chunk may cross the end of the array (so some elements from the end, then some elements from the beginning).        

        index: Where the chunk starts, on which operation can be done; must be in the range [-n, n) where n is the number of crossings in the braid (so n = len(braid))
        """
        if self.is_braid_relation2_performable(index):
            # Since braid is circular, we make sure index is negative, so we can't get an out of bounds error if `index = len(self._braid) - 1`.
            if index >= 0:
                index -= len(self._braid)
            transformed_braid = self._braid.copy()
            transformed_braid[index], transformed_braid[index+1] = transformed_braid[index+1], transformed_braid[index]

            return Braid(transformed_braid, copy_sigmas=False)
        else:
            raise IllegalTransformationException

    #Markov moves
    def conjugation(self,value: int,index: int) -> 'Braid':
        """
        Conjugates the braid with sigma indexed by index1, inserts a index sigma indexed by index1 and -index1 to the index index2
        index1: int in within the interval [-(n-1),n-1], not equal to zero
        index2: int in within the interval [0, n]
        """
        """
        assert index != 0, "Index should not be zero"
        assert abs(index)<self._n, f"Index should be less than {self._n}"
        assert type(index) is int, "Provided index should be integer"
        """
        if self.is_conjugation_performable(value, index):
            
            if index == len(self) + 1:
                conjugated_braid = np.concatenate((np.array([-value]),self._braid,np.array([value])))
            else:
                conjugated_braid = np.concatenate((self._braid[:index], np.array([value, -value]), self._braid[index:]))

            return Braid(conjugated_braid, copy_sigmas=False)
        else:
            raise IllegalTransformationException

    def stabilization(self,inverse: bool = False) -> 'Braid':
        """
        Performs stabilization move.
        """
        if inverse:
            braid_stabilized = np.concatenate((self._braid,np.array([-self._n])))
        else:
            braid_stabilized = np.concatenate((self._braid,np.array([self._n])))

        return Braid(braid_stabilized, copy_sigmas=False)

    def destabilization(self) -> 'Braid':
        """
        Performs destabilization move.
        """
        if self.is_destabilization_performable() :
            braid_destabilized = self._braid[:-1].copy()

            return Braid(braid_destabilized, copy_sigmas=False)

        else:
            raise IllegalTransformationException
    
    def remove_sigma_inverse_pair(self,index: int) -> 'Braid':
        """
        Remove consequtive inverse on a given place (last and first element are consequtive)
        index: the smaller index (or when the pair is the last and first then it is the last index)
        """
        if self.is_remove_sigma_inverse_pair_performable(index):
            if index == 0:
                modified_braid = self._braid[2:]
            elif index == len(self) - 2:
                modified_braid = self._braid[:-2]
            elif index == len(self) - 1:
                modified_braid = self._braid[1:-1]
            else:
                modified_braid = np.concatenate((self._braid[:(index)], self._braid[(index + 2):]))
            return Braid(modified_braid)
        else:
            raise IllegalTransformationException


    #Chech whether a move is performable or not
    def is_braid_relation1_performable(self,index: int) -> bool:
        """
        Check if braid relation 1 is performable at the index. See documentation of `braid_relation1` for details.

        index: Where the chunk would start; in the range [-n, n) where n is the number of crossings in the braid (so n = len(braid))
        """
        if len(self._braid) < 3:
            return False
        if index >= 0:
            index -= len(self)
        return len(self) != 0 and abs(self._braid[index]) == abs(self._braid[index+2]) and abs(abs(self._braid[index+1]) - abs(self._braid[index])) == 1 and not (np.sign(self._braid[index+1]) != np.sign(self._braid[index]) and np.sign(self._braid[index+1]) != np.sign(self._braid[index+2]))
    
    def braid_relation1_performable_indices(self) -> np.ndarray:
        """
        Returns array of indices where braid relation 1 is performable. See documentation of member function `braid_relation1` for details.

        returns: indices in the range [0, n) where n is the number of crossings in the braid (so n = len(braid))
        """
        positions = []
        for index in range(len(self._braid)):
            if self.is_braid_relation1_performable(index):
                positions.append(index)
        return np.array(positions)

    def is_braid_relation2_performable(self,index: int) -> bool:
        if index >= len(self._braid):
            raise IndexOutOfRangeException(f"index = {index} too large, at least the number of crossings = {len(self._braid)}")
        if index < -len(self._braid):
            raise IndexOutOfRangeException(f"index = {index} too small, smaller than number of crossings * (-1) = {-len(self._braid)}")
        
        # Since braid is circular, we make sure index is negative, so we can't get an out of bounds error if `index = len(self._braid) - 1`.
        if index >= 0:
            index -= len(self._braid)
        return len(self) != 0 and abs(abs(self._braid[index]) - abs(self._braid[index+1])) >= 2
    
    def braid_relation2_performable_indices(self) -> np.ndarray:
        if len(self._braid) == 0:
            return np.array([])

        positions = np.where(1<np.abs(np.diff(np.abs(self._braid),append=abs(self._braid[0]))))[0]
        return positions

    def is_conjugation_performable(self,value: int, index: int) -> bool:
        return value != 0 and self._n>abs(value) and 0 <= index and index <= len(self) + 1
    
    def is_destabilization_performable(self) -> bool:
        return len(self) != 0 and abs(self._braid[-1]) == self._n - 1 and (not np.any(abs(self._braid[:-1]) == self._n - 1))
    
    def is_remove_sigma_inverse_pair_performable(self,index: int) -> bool:
        return len(self) != 0 and (self._braid[index] + self._braid[(index+1)%len(self)] == 0)
    
    def remove_sigma_inverse_pair_performable_indices(self) -> np.ndarray:
        indices = np.array([
            i for i in range(len(self))
            if self.is_remove_sigma_inverse_pair_performable(i)])

        return indices
    
    def performable_moves(self) -> list[BraidTransformation]:
        """
        Checks if a move is performable.
        move: The name of the move to check, e.g., "shift_left", "braid_relation1", etc.
        index: Optional index parameter required for some moves.
        Returns: True if the move is performable, otherwise False.
        """
        performable_moves: list[BraidTransformation] = [self.shift_left,self.shift_right,partial(self.stabilization,inverse=True), partial(self.stabilization,inverse=False)] #Always performable

        if self.is_destabilization_performable():
            performable_moves.append(self.destabilization)
        
        conjugation_values = list(range(-self._n+1,0)) + list(range(1,self._n))
        conjugation_indices = (range(0, len(self) + 2))
        conjugation_performable_moves: list[BraidTransformation] = []
        for v in conjugation_values:
            for i in conjugation_indices:
                if self.is_conjugation_performable(v, i):
                    conjugation_performable_moves = conjugation_performable_moves + [partial(self.conjugation,value=v,index=i)]

        performable_moves = performable_moves + conjugation_performable_moves

        braid_relation1_indices = self.braid_relation1_performable_indices()
        braid_relation1_performable_moves: list[BraidTransformation] = [partial(self.braid_relation1,index=i) for i in braid_relation1_indices]

        performable_moves = performable_moves + braid_relation1_performable_moves

        braid_relation2_indices = self.braid_relation2_performable_indices()
        braid_relation2_performable_moves: list[BraidTransformation] = [partial(self.braid_relation2,index=i) for i in braid_relation2_indices]

        performable_moves = performable_moves + braid_relation2_performable_moves

        braid_remove_sigma_inverse_pairs = self.remove_sigma_inverse_pair_performable_indices()
        braid_remove_sigma_inverse_pair_moves: list[BraidTransformation] = [partial(self.remove_sigma_inverse_pair,index=i) for i in braid_remove_sigma_inverse_pairs]

        performable_moves = performable_moves + braid_remove_sigma_inverse_pair_moves

        return performable_moves

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Braid):
            return NotImplemented
        return self._n == value._n and np.array_equal(self._braid, value._braid)
    
    def __len__(self) -> int:
        return len(self._braid)
