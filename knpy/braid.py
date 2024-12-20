# pylint: disable=R0801
from typing import Callable
import numpy as np
import torch
import braidvisualiser as bv
from functools import partial
from .data_utils import knots_in_braid_notation_dict
from .exceptions import IllegalTransformationException, InvalidBraidException, IndexOutOfRangeException

type BraidNotation = np.ndarray
type BraidTransformation = Callable[[], "Braid"]


class Braid:
    def __init__(self, sigmas: np.ndarray | list[int] | str, notation_index: int = 0, copy_sigmas: bool = True):
        """
        Init Braid class, sigmas should not contain zero or bigger value than n_strands

        sigmas: Braid notation, e.g. [1,-1,2] or the string name of knot e.g. 4_1 #TODO Above 10 there a and n knots
            (e.g. 11a,13n)
        notation_index: If sigmas is a name of braid than it is possible that multiple notations are available to the
            same knot. notation_index says which one to choose from these.
        #TODO 10_136 {{-1;-1;-2;3;-2;1;-2;-2;3;2;2};{-1;2;-1;2;3;-2;-2;-4;3;-4}}? Which one?
        #TODO 11n_8,{{-1;-1;-2;1;-2;-1;3;-2;-2;-4;3;-4};{1;2;-1;2;3;-2;-1;-1;-2;-2;-3;-3;-2}}? Which one?
        """
        self._braid: BraidNotation
        if isinstance(sigmas, str):
            self._braid = np.array(knots_in_braid_notation_dict[sigmas][notation_index], dtype=np.int32)
        elif isinstance(sigmas, np.ndarray):
            if copy_sigmas:
                self._braid = sigmas.copy()
            else:
                self._braid = sigmas
        else:
            if not all(isinstance(x, (int, np.integer)) for x in sigmas):
                raise InvalidBraidException(
                    f"Unable to create braid from {type(sigmas)}, an element is not instance of int or np.integer"
                )
            self._braid = np.array(sigmas, dtype=np.int32)

        if np.any(self._braid == 0):
            raise InvalidBraidException

        if len(self) == 0:
            self._n = 1
        else:
            self._n = np.max(np.abs(self._braid)) + 1

    def values(self) -> tuple[int, BraidNotation]:
        """
        Returns (self._n,self._braid) values as tuple
        """
        return (self._n, self._braid.copy())

    def notation(self, copy=True) -> BraidNotation:
        """
        Returns numpy array of sigmas
        """
        if copy:
            return self._braid.copy()
        else:
            return self._braid

    @property
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

    # Action functions from paper https://arxiv.org/pdf/2010.16263

    def shift_left(self, amount: int = 1) -> "Braid":
        """
        Shifts the crossings of the braid left. Numbering the original crossings as `[0, 1, 2, ..., n - 1]` it
        transforms it to `[amount, amount + 1, amount + 2, ..., n - 2, n - 1, 0, 1, 2, ..., amount - 1]`.

        amount: in the range (-n, n) where n is the number of crossings in the braid (so n = len(braid))
        """

        if amount >= len(self._braid) or amount <= -len(self._braid):
            raise IllegalTransformationException(
                f"amount = {amount} not in range ({-len(self._braid)}, {len(self._braid)})"
            )

        left_shifted_braid = np.concatenate((self._braid[amount:], self._braid[:amount]))
        return Braid(left_shifted_braid, copy_sigmas=False)

    def shift_right(self, amount: int = 1) -> "Braid":
        """
        Shifts the crossings of the braid right. Same as shifting left by the negative amount.
        amount: in the range (-n, n) where n is the number of crossings in the braid (so n = len(braid))
        """

        if amount >= len(self._braid) or amount <= -len(self._braid):
            raise IllegalTransformationException(
                f"amount = {amount} not in range ({-len(self._braid)}, {len(self._braid)})"
            )

        return self.shift_left(-amount)

    # Braid relations
    def braid_relation1(self, index: int) -> "Braid":
        """
        Perform first braid relation.

        Maps between chunks `[±a, ±(a + 1), ±a] ↔ [±(a + 1), ±a, ±(a + 1)]`, `[∓a, ±(a + 1), ±a] ↔ [±(a + 1), ±a, ∓(a +
        1)]` and `[±a, ±(a + 1), ∓a] ↔ [∓(a + 1), ±a, ±(a + 1)]` (where all `±` have the same sign and all `∓` have the
        opposite). `[±a, ∓(a + 1), ±a] ↔ [±(a + 1), ∓a, ±(a + 1)]` is NOT allowed.

        The elements of the chuck must be distict, so the braid must consist of at least 3 crossings. The braid is
        assumed to be circular, the chunk may cross the end of the array (so some elements from the end, then some
        elements from the beginning).

        index: Where the chunk starts, on which operation can be done; in the range [-n, n) where n is the number of
        crossings in the braid (so n = len(braid))
        """
        if self.is_braid_relation1_performable(index):
            signs = np.ones(3)
            if index > 0:
                index -= len(self._braid)
            signs[self._braid[[index, index + 1, index + 2]] < 0] = -1
            transformed_braid = self._braid.copy()
            transformed_braid[[index, index + 1, index + 2]] = (
                abs(self._braid)[[index + 1, index, index + 1]]
            ) * signs[::-1]

            return Braid(transformed_braid, copy_sigmas=False)
        else:
            raise IllegalTransformationException(f"Braid relation 1 is not performable at index {index}")

    def braid_relation2(self, index: int) -> "Braid":
        """
        Perform second braid relation.

        Maps between the chunks `[i, j] ↔ [j, i]` if `abs(abs(i) - abs(j)) >= 2`.

        The elements of the chuck must be distict, so the braid must consist of at least 2 crossings. The braid is
        assumed to be circular, the chunk may cross the end of the array (so some elements from the end, then some
        elements from the beginning).

        index: Where the chunk starts, on which operation can be done; must be in the range [-n, n) where n is the
            number of crossings in the braid (so n = len(braid))
        """
        if self.is_braid_relation2_performable(index):
            # Since braid is circular, we make sure index is negative, so we can't get an out of bounds error if
            # `index = len(self._braid) - 1`.
            if index >= 0:
                index -= len(self._braid)
            transformed_braid = self._braid.copy()
            transformed_braid[index], transformed_braid[index + 1] = (
                transformed_braid[index + 1],
                transformed_braid[index],
            )

            return Braid(transformed_braid, copy_sigmas=False)
        else:
            raise IllegalTransformationException(f"Braid relation 2 is not performable at index {index}")

    # Markov moves
    def conjugation(self, value: int, index: int) -> "Braid":
        """
        Conjugates the braid with sigma indexed by index1, inserts a index sigma indexed by index1 and -index1 to the
        index index2

        value: Inserts sigmas `σ_{value} σ_{-value}`. Must be in the range `(-n, n)` and not zero where n is the number
            of threads (so `n = braid.values()[0]`).
        index: When the index is less than k where k is the number of crossings, it inserts them before the k-th sigma.
            When index is k it inserts them at the end. When index is k + 1, it inserts `σ_{value}` at the end and
            `ο_{-value}` at the beginning. Must be in rangee `[0, k +1]` (negative value are explicitly not allowed
            here).

        Example. Let's denote the existing sigmas as `0 1 2`, value as `a` then depending on the index the result will
        be:

        ```
        0: a -a 0 1 2
        1: 0 a -a 1 2
        2: 0 1 a -a 2
        3: 0 1 2 a -a
        4: -a 0 1 2 a
        ```
        """
        # This should not be needed as `is_conjugation_performable` should always return True or raise an exception, but
        # is kept here to be sure.
        if self.is_conjugation_performable(value, index):

            if index == len(self) + 1:
                conjugated_braid = np.concatenate((np.array([-value]), self._braid, np.array([value])))
            else:
                conjugated_braid = np.concatenate((self._braid[:index], np.array([value, -value]), self._braid[index:]))

            return Braid(conjugated_braid, copy_sigmas=False)
        else:
            raise IllegalTransformationException(f"Conjugation is not performable at index {index}")

    def stabilization(self, index: int | None = None, on_top=False, inverse: bool = False) -> "Braid":
        """
        Performs stabilization move before specified crossing index, either
        at the top or bottom thread, inserting either a positive or negative
        braid generator.
        """

        if index is None:
            index = self._braid.shape[0]

        assert isinstance(index, int)

        if index < 0 or index > self._braid.shape[0]:
            raise IndexOutOfRangeException("Index must be between 0 and length of braid")

        braid_stabilized = self._braid.copy()
        if inverse:
            new_sigma = -1
        else:
            new_sigma = +1

        if on_top:
            braid_stabilized += np.sign(braid_stabilized)
            braid_stabilized = np.insert(braid_stabilized, index, new_sigma)
        else:
            new_sigma = new_sigma * self.strand_count
            braid_stabilized = np.insert(braid_stabilized, index, new_sigma)

        return Braid(braid_stabilized, copy_sigmas=False)

    def destabilization(self, index: int) -> "Braid":
        """
        Performs destabilization move at given index location, results in
        a braid with one fewer crossings and one fewer strands.
        """
        if self.is_destabilization_performable(index):
            on_top = abs(self._braid[index]) == 1
            braid_destabilized = np.delete(self._braid, [index])
            if on_top:
                braid_destabilized -= np.sign(braid_destabilized)
            return Braid(braid_destabilized, copy_sigmas=False)
        else:
            raise IllegalTransformationException(f"Destabilization is not performable at index {index}")

    def remove_sigma_inverse_pair(self, index: int) -> "Braid":
        """
        Remove consequtive inverse on a given place (last and first element are consequtive)

        index: the smaller index (or when the pair is the last and first then it is the last index); must be in the
            range [-k, k) where k is the number of crossings (so `len(braid)`).
        """
        if self.is_remove_sigma_inverse_pair_performable(index):
            if index < 0:
                index += len(self)

            if index == 0:
                modified_braid = self._braid[2:]
            elif index == len(self) - 2:
                modified_braid = self._braid[:-2]
            elif index == len(self) - 1:
                modified_braid = self._braid[1:-1]
            else:
                modified_braid = np.concatenate((self._braid[:(index)], self._braid[(index + 2) :]))
            return Braid(modified_braid)
        else:
            raise IllegalTransformationException(f"Sigma inverse pair is not removable at index {index}")

    # Chech whether a move is performable or not
    def is_braid_relation1_performable(self, index: int) -> bool:
        """
        Check if braid relation 1 is performable at the index. See documentation of `braid_relation1` for details.

        index: Where the chunk would start; in the range [-n, n) where n is the number of crossings in the braid (so n =
            len(braid))
        """
        if len(self._braid) < 3:
            return False
        if index >= 0:
            index -= len(self)
        return (
            len(self) != 0
            and abs(self._braid[index]) == abs(self._braid[index + 2])
            and abs(abs(self._braid[index + 1]) - abs(self._braid[index])) == 1
            and not (
                np.sign(self._braid[index + 1]) != np.sign(self._braid[index])
                and np.sign(self._braid[index + 1]) != np.sign(self._braid[index + 2])
            )
        )

    def braid_relation1_performable_indices(self) -> np.ndarray:
        """
        Returns array of indices where braid relation 1 is performable. See documentation of member function
        `braid_relation1` for details.

        returns: indices in the range [0, n) where n is the number of crossings in the braid (so n = len(braid))
        """
        positions = []
        for index in range(len(self._braid)):
            if self.is_braid_relation1_performable(index):
                positions.append(index)
        return np.array(positions)

    def is_braid_relation2_performable(self, index: int) -> bool:
        if index >= len(self._braid):
            raise IndexOutOfRangeException(
                f"index = {index} too large, at least the number of crossings = {len(self._braid)}"
            )
        if index < -len(self._braid):
            raise IndexOutOfRangeException(
                f"index = {index} too small, smaller than number of crossings * (-1) = {-len(self._braid)}"
            )

        # Since braid is circular, we make sure index is negative, so we can't get an out of bounds error if `index =
        # len(self._braid) - 1`.
        if index >= 0:
            index -= len(self._braid)
        return len(self) != 0 and abs(abs(self._braid[index]) - abs(self._braid[index + 1])) >= 2

    def braid_relation2_performable_indices(self) -> np.ndarray:
        if len(self._braid) == 0:
            return np.array([])

        positions = np.where(1 < np.abs(np.diff(np.abs(self._braid), append=abs(self._braid[0]))))[0]
        return positions

    def is_conjugation_performable(self, value: int, index: int) -> bool:
        """
        See documentation conjugation member function for details.

        Note: this function either returns true or raises an exception.
        """
        if value == 0:
            raise ValueError("Sigma can't be zero")
        if value <= -self._n or value >= self._n:
            raise ValueError(
                f"Sigma (σ_{{{value}}}) must be in range (-n, n) where n is the number of threads "
                f"(so `n = braid.values()[0]`)."
            )
        if index < 0:
            raise IndexOutOfRangeException("Negative indexes are not allowed for conjugation")
        if index > len(self._braid) + 1:
            raise IndexOutOfRangeException(
                f"Conjugation index (currently {index}) can be at most the number of crossings + 1 = {len(self._braid)}"
            )

        return True

    def is_destabilization_performable(self, index: int) -> bool:
        """
        Helper function to determine if destabilisation move is performable
        at given index location, at either the top or bottom strand.
        """
        valid_index = 0 <= index < self._braid.shape[0]
        bottom_removable = np.array_equal(np.where(np.abs(self._braid) == self.strand_count - 1)[0], np.array([index]))
        top_removable = np.array_equal(np.where(np.abs(self._braid) == 1)[0], np.array([index]))
        return valid_index and (bottom_removable or top_removable)

    def is_remove_sigma_inverse_pair_performable(self, index: int) -> bool:
        if index < -len(self):
            raise IndexOutOfRangeException(f"index = {index} too small, must by at least -length = {-len(self)}")
        if index >= len(self):
            raise IndexOutOfRangeException(f"index = {index} too large, must be less than length = {len(self)}")

        return len(self) != 0 and (self._braid[index] + self._braid[(index + 1) % len(self)] == 0)

    def remove_sigma_inverse_pair_performable_indices(self) -> np.ndarray:
        indices = np.array([i for i in range(len(self)) if self.is_remove_sigma_inverse_pair_performable(i)])

        return indices

    def performable_moves(self) -> list[BraidTransformation]:
        """
        Checks if a move is performable.
        move: The name of the move to check, e.g., "shift_left", "braid_relation1", etc.
        index: Optional index parameter required for some moves.
        Returns: True if the move is performable, otherwise False.
        """
        performable_moves: list[BraidTransformation] = []

        for i in range(0, len(self)):
            if self.is_destabilization_performable(i):
                performable_moves.extend([partial(self.destabilization, i)])

        for i in range(0, len(self) + 1):
            performable_moves.extend([partial(self.stabilization, index=i, on_top=False, inverse=False)])
            performable_moves.extend([partial(self.stabilization, index=i, on_top=False, inverse=True)])
            performable_moves.extend([partial(self.stabilization, index=i, on_top=True, inverse=False)])
            performable_moves.extend([partial(self.stabilization, index=i, on_top=True, inverse=True)])

        conjugation_values = list(range(-self._n + 1, 0)) + list(range(1, self._n))
        conjugation_indices = range(0, len(self) + 2)
        conjugation_performable_moves: list[BraidTransformation] = []
        for v in conjugation_values:
            for i in conjugation_indices:
                if self.is_conjugation_performable(v, i):
                    conjugation_performable_moves = conjugation_performable_moves + [
                        partial(self.conjugation, value=v, index=i)
                    ]

        performable_moves += conjugation_performable_moves

        braid_relation1_indices = self.braid_relation1_performable_indices()
        braid_relation1_performable_moves: list[BraidTransformation] = [
            partial(self.braid_relation1, index=i) for i in braid_relation1_indices
        ]

        performable_moves += braid_relation1_performable_moves

        braid_relation2_indices = self.braid_relation2_performable_indices()
        braid_relation2_performable_moves: list[BraidTransformation] = [
            partial(self.braid_relation2, index=i) for i in braid_relation2_indices
        ]

        performable_moves += braid_relation2_performable_moves

        braid_remove_sigma_inverse_pairs = self.remove_sigma_inverse_pair_performable_indices()
        braid_remove_sigma_inverse_pair_moves: list[BraidTransformation] = [
            partial(self.remove_sigma_inverse_pair, index=i) for i in braid_remove_sigma_inverse_pairs
        ]

        performable_moves += braid_remove_sigma_inverse_pair_moves

        return performable_moves

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Braid):
            return NotImplemented
        return self._n == value._n and np.array_equal(self._braid, value._braid)

    def __len__(self) -> int:
        return len(self._braid)
