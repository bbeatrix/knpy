import sys
import os
import pytest
import numpy as np
#IMPORTANT: knpy should be installed first
from knpy import Braid
from knpy import IllegalTransformationException, InvalidBraidException, IndexOutOfRangeException

class TestBraidClassBraidRelationsInit:
    def test_init_empty(self):
        braid = Braid([])
        assert braid._n == 1
        assert braid._braid.shape[0] == 0
    
    def test_init(self):
        braid = Braid([1,2,3])
        assert braid._n == 4
        assert braid._braid.shape[0] == 3
    
    def test_init_from_database(self):
        braid = Braid("3_1")
        assert braid._n == 2
        assert braid._braid.shape[0] == 3
        assert np.all(braid._braid == np.array([1,1,1]))
    
    def test_values(self):
        braid = Braid([1,2,3])
        assert braid._n == braid.values()[0]
        assert braid._braid.shape[0] == braid.values()[1].shape[0]

    def test_init_exception(self):
        with pytest.raises(InvalidBraidException):
            braid = Braid([1,0,-1,2,3])


class TestBraidClassBraidRelationsStabilizationDestabilization:
    def test_is_destabilization_performable_empty(self):
        braid = Braid([])
        assert not braid.is_destabilization_performable()
    
    def test_is_destabilization_performable_true1(self):
        braid = Braid([1, -2, 3, 4])
        assert braid.is_destabilization_performable()
    
    def test_is_destabilization_performable_true2(self):
        braid = Braid([1, -2, -3])
        assert braid.is_destabilization_performable()
    
    def test_is_destabilization_performable_false1(self):
        braid = Braid([-3, 1, -2, -3])
        assert not braid.is_destabilization_performable()

    def test_is_destabilization_performable_false2(self):
        braid = Braid([ 1, -2, -3, 1])
        assert not braid.is_destabilization_performable()

    def test_is_destabilization_performable_false3(self):
        braid = Braid([ 1, -2, -3, 1, 4, -4])
        assert not braid.is_destabilization_performable()

    def test_stabilization_empty(self):
        braid = Braid([])
        braid.stabilization()
        assert braid.values()[0] == 2
        assert braid.values()[1][-1] == 1
        assert len(braid.values()[1]) == 1

    def test_stabilization(self):
        braid = Braid([1, -2, 3])
        braid.stabilization()
        assert braid.values()[0] == 5
        assert braid.values()[1][-1] == 4
        assert len(braid.values()[1]) == 4

    def test_stabilization_inverse(self):
        braid = Braid([1, -2, 3])
        braid.stabilization(inverse=True)
        assert braid.values()[0] == 5
        assert braid.values()[1][-1] == -4
        assert len(braid.values()[1]) == 4

    def test_destabilization_empty(self):
        braid = Braid([])
        with pytest.raises(IllegalTransformationException):
            braid.destabilization() 


    def test_destabilization(self):
        braid = Braid([1, -2, 3])
        braid.destabilization()
        assert braid.values()[0] == 3
        assert len(braid.values()[1]) == 2
    
    def test_destabilization_inverse(self):
        braid = Braid([1, -2, -3])
        braid.destabilization()
        assert braid.values()[0] == 3
        assert len(braid.values()[1]) == 2

    def test_destabilization_exception(self):
        braid = Braid([-3 ,1, -2, 3])
        with pytest.raises(IllegalTransformationException):
            braid.destabilization() 

class TestBraidClassBraidRelationsConjugation:
    def test_is_conjugation_performable_empty(self):
        braid = Braid([])
        assert not braid.is_conjugation_performable(value=1, index=0)
        assert not braid.is_conjugation_performable(value=1, index=1)

    def test_is_conjugation_performable_true1(self):
        braid = Braid([1, -2, 3, 4])
        assert braid.is_conjugation_performable(value=1, index=4)
    
    def test_is_conjugation_performable_true2(self):
        braid = Braid([1, -2, 3, 4])
        assert braid.is_conjugation_performable(value=-2, index=4)

    def test_is_conjugation_performable_inbetween_true1(self):
        braid = Braid([1, -2, 3, 4])
        assert braid.is_conjugation_performable(value=1, index=2)
    
    def test_is_conjugation_performable_false1(self):
        braid = Braid([1, -2, 3, 4])
        assert not braid.is_conjugation_performable(value=0, index=4)
    
    def test_is_conjugation_performable_false2(self):
        braid = Braid([1, -2, 3, 4])
        assert not braid.is_conjugation_performable(value=-5, index=12)

    def test_is_conjugation_performable_false3(self):
        braid = Braid([1, -2, 3, 4])
        assert not braid.is_conjugation_performable(value=5, index=4)
    
    def test_is_conjugation_performable_inbetween_false1(self):
        braid = Braid([1, -2, 3, 4])
        assert not braid.is_conjugation_performable(value=1, index=-1)
    
    def test_is_conjugation_performable_inbetween_false2(self):
        braid = Braid([1, -2, 3, 4])
        assert not braid.is_conjugation_performable(value=1, index=6)

    def test_conjugation_empty(self):
        braid = Braid([])
        with pytest.raises(IllegalTransformationException):
            braid.conjugation(value=0, index=0) 

    def test_conjugation(self):
        braid = Braid([-1, -2, 3, 4])
        values = braid.conjugation(value=1, index=5)
        print(values)
        assert values[0] == -1 and values[-1] == 1
    
    def test_conjugation1(self):
        braid = Braid([-1, -2, 3, 4])
        values = braid.conjugation(value=2, index=4)
        print(values)
        assert values[-2] == 2 and values[-1] == -2

    def test_conjugation2(self):
        braid = Braid([-1, -2, 5, 6])
        values = braid.conjugation(value=-4, index=5)
        print(values)
        assert values[0] == 4 and values[-1] == -4

    def test_conjugation3(self):
        braid = Braid([-1, -2, 7, 6])
        values = braid.conjugation(value=5, index=4)
        assert values[-2] == 5 and values[-1] == -5

    def test_conjugation_inverse(self):
        braid = Braid([-1, -2, 3, 4])
        values = braid.conjugation(value=-4, index=4)
        assert values[-2] == -4 and values[-1] == 4
    
    def test_conjugation_inbetween1(self):
        braid = Braid([-1, -2, 3, 4])
        values = braid.conjugation(value=1, index=0)
        assert values[0] == 1 and values[1] == -1
    
    def test_conjugation_inbetween2(self):
        braid = Braid([-1, -2, 3, 4])
        values = braid.conjugation(value=2, index=3)
        assert values[3] == 2 and values[4] == -2

    def test_conjugation_inverse_inbetween(self):
        braid = Braid([-1, -2, 3, 4])
        values = braid.conjugation(value=-4, index=2)
        assert values[2] == -4 and values[3] == 4

    def test_conjugation_exception(self):
        braid = Braid([-1, -2, 3, 4])
        with pytest.raises(IllegalTransformationException):
            braid.conjugation(value=5, index=4)

class TestBraidClassBraidRelationsBraidRelation1:
    
    def test_is_braid_relation1_performable_empty(self):
        braid = Braid([])
        assert not braid.is_braid_relation1_performable(index = 0)
    
    def test_is_braid_relation1_performable_short(self):
        braid = Braid([1, 2])
        assert not braid.is_braid_relation1_performable(index = 0)
    
    def test_is_braid_relation1_performable_only_true(self):
        braid = Braid([1,2,1])
        assert braid.is_braid_relation1_performable(index = 0)

    def test_is_braid_relation1_performable_middle_true(self):
        braid = Braid([9,3,4,3,3,5])
        assert braid.is_braid_relation1_performable(index = 1)
    
    def test_is_braid_relation1_performable_negatives_true(self):
        braid = Braid([1,-2,-1,3,3,5])
        assert braid.is_braid_relation1_performable(index = 0)
    
    def test_is_braid_relation1_performable_end_true(self):
        braid = Braid([9,3,3,5,4,3,4])
        assert braid.is_braid_relation1_performable(index = 4)

    def test_is_braid_relation1_performable_beginning_true(self):
        braid = Braid([-5,-4,-5,1,2])
        assert braid.is_braid_relation1_performable(index = 0)

    def test_is_braid_relation1_performable_multiple_true(self):
        braid = Braid([-5,-4,-5,1,2,1,-2,-1])
        assert braid.is_braid_relation1_performable(index = 0)
        assert braid.is_braid_relation1_performable(index = 3) 
        assert braid.is_braid_relation1_performable(index = 4)

    def test_is_braid_relation1_performable_false1(self):
        braid = Braid([9,3,3,1,1,1])
        assert not braid.is_braid_relation1_performable(index = 3)

    def test_is_braid_relation1_performable_false2(self):
        braid = Braid([9,3,3,5,3,1])
        assert not braid.is_braid_relation1_performable(index = 0)
    
    def test_is_braid_relation1_performable_opposite_false(self):
        braid = Braid([9,3,3,-5,4,-5,1,2])
        assert not braid.is_braid_relation1_performable(index = 3)

    def test_is_braid_relation1_performable_mixed(self):
        braid = Braid([2, 2, 1, -2, 1])
        for i in range(len(braid.values()[1])):
            assert braid.is_braid_relation1_performable(i) == (i in [1, 3])
    
    def test_is_braid_relation1_performable_mixed_negative(self):
        braid = Braid([2, 2, 1, -2, 1])
        for i in range(len(braid.values()[1]), 0):
            assert braid.is_braid_relation1_performable(i) == (i in [-4, -2])
    
    def test_is_braid_relation1_performable_indices_empty(self):
        braid = Braid([])
        assert braid.braid_relation1_performable_indices().shape[0] == 0

    def test_braid_relation1_preformable_indices_empty(self):
        braid = Braid([9,3,3,1,1,1])
        assert braid.braid_relation1_performable_indices().shape[0] == 0 

    def test_braid_relation1_performable_indices_short(self):
        braid = Braid([1, 2])
        assert (braid.braid_relation1_performable_indices() == []).all()  
    
    def test_braid_relation1_preformable_indices_one(self):
        braid = Braid([1,2,1])
        performable_indices = braid.braid_relation1_performable_indices()
        assert performable_indices.shape[0] == 1
        assert performable_indices[0] == 0

    def test_braid_relation1_preformable_indices_multiple(self):
        braid = Braid([-5,-4,-5,1,2,1,-2,-1])
        performable_indices = braid.braid_relation1_performable_indices()
        assert np.array_equal(performable_indices, np.array([0, 3, 4, 5]))

    def test_braid_relation1_empty(self):
        braid = Braid([])
        with pytest.raises(IllegalTransformationException):
            braid.braid_relation1(index=0)

    def test_braid_relation1_all_same_sign(self):
        braid = Braid([3, 2, 1, 2])
        assert (braid.braid_relation1(1, inplace=False) == [3, 1, 2, 1]).all()

    def test_braid_relation1_last_sign_different(self):
        braid = Braid([3, 2, 1, -2])
        assert (braid.braid_relation1(1, inplace=False) == [3, -1, 2, 1]).all()

    def test_braid_relation1_circular(self):
        braid = Braid([1, -2, 3, 2])
        assert (braid.braid_relation1(3, inplace=False) == [2, 1, 3, -1]).all()

    def test_braid_relation1_negative_index_inside(self):
        braid = Braid([3, 2, 1, 2])
        assert (braid.braid_relation1(-3, inplace=False) == [3, 1, 2, 1]).all()

    def test_braid_relation1_negative_index_boundary(self):
        braid = Braid([1, 2, 3, 2])
        assert (braid.braid_relation1(-1, inplace=False) == [2, 1, 3, 1]).all()

    def test_braid_relation1_short(self):
        braid = Braid([1, 2])
        with pytest.raises(IllegalTransformationException):
            braid.braid_relation1(0)

    def test_braid_relation1_inplace(self):
        braid = Braid([3, 2, 1, 2])
        braid.braid_relation1(1)
        assert braid == Braid([3, 1, 2, 1])
    
    def test_braid_relation1_not_inplace_does_not_modify(self):
        braid = Braid([3, 2, 1, 2])
        new_braid = braid.braid_relation1(1, inplace=False)
        assert (new_braid == [3, 1, 2, 1]).all()
        assert braid == Braid([3, 2, 1, 2])

class TestBraidClassBraidRelationsBraidRelation2:
    
    def test_is_braid_relation2_performable_empty(self):
        braid = Braid([])
        assert not braid.is_braid_relation2_performable(index = 0)
    
    def test_is_braid_relation2_performable_indices_empty(self):
        braid = Braid([])
        assert braid.braid_relation2_performable_indices().shape[0] == 0
    
    def test_braid_relation2_empty(self):
        braid = Braid([])
        with pytest.raises(IllegalTransformationException):
            braid.braid_relation2(index=0)

    def test_braid_relation2_abs_check1(self):
        braid = Braid([1, 3, -3, 1])
        assert np.all(braid.braid_relation2_performable_indices() == np.array([0, 2]))

    def test_braid_relation2_abs_check2(self):
        braid = Braid([1, 3, -1, -2, 4])
        assert np.all(braid.braid_relation2_performable_indices() == np.array([0, 1, 3]))

    def test_braid_relation2_one_element(self):
        braid = Braid([10])
        assert np.all(braid.braid_relation2_performable_indices() == np.array([]))

    def test_braid_relation2_negative_exception(self):
        braid = Braid([1, -3, 2])
        for i in range(1, 5):
            with pytest.raises(IllegalTransformationException):
                braid.braid_relation2(-i)
            

    def test_braid_relation2_big_index_exception(self):
        braid = Braid([1, -3, 2])
        for i in range(5):
            with pytest.raises(IllegalTransformationException):
                braid.braid_relation2(2+i)


class TestBraidClassBraidRelationsShifts:
    
    def test_shift_left_empty(self):
        braid = Braid([])
        braid.shift_left()
        assert braid.values()[1].shape[0] == 0
    
    def test_shift_right_empty(self):
        braid = Braid([])
        braid.shift_right()
        assert braid.values()[1].shape[0] == 0
    
    def test_shift_left_with_amount_empty(self):
        braid = Braid([])
        braid.shift_left_with_amount(amount=2)
        assert braid.values()[1].shape[0] == 0
    
    def test_shift_right_with_amount_empty(self):
        braid = Braid([])
        braid.shift_right_with_amount(amount=2)
        assert braid.values()[1].shape[0] == 0


class TestBraidClassBraidRelationsRemoveSigmaAndInverse:
    
    def test_is_remove_sigma_inverse_pair_performable_empty(self):
        braid = Braid([])
        assert not braid.is_remove_sigma_inverse_pair_performable(index=0)
    
    def test_remove_sigma_inverse_pair_performable_indices_empty(self):
        braid = Braid([])
        assert braid.remove_sigma_inverse_pair_performable_indices().shape[0] == 0
    
    def test_remove_sigma_inverse_pair_empty(self):
        braid = Braid([])
        with pytest.raises(IllegalTransformationException):
            braid.remove_sigma_inverse_pair(index=0)

    def test_is_remove_sigma_inverse_pair_performable_one_element(self):
        braid = Braid([1])
        assert not braid.is_remove_sigma_inverse_pair_performable(index = 0)

    def test_is_remove_sigma_inverse_pair_performable_true(self):
        braid = Braid([2, 1, -1])
        assert braid.is_remove_sigma_inverse_pair_performable(index=1)

    def test_is_remove_sigma_inverse_pair_performable_false(self):
        braid = Braid([2, 1, -1, -2])
        assert not braid.is_remove_sigma_inverse_pair_performable(index=0)
    
    def test_remove_sigma_inverse_pair1(self):
        braid = Braid([2, 1, -1, 3])
        values = braid.remove_sigma_inverse_pair(index=1)._braid
        assert values[0] == 2 and values[1] == 3

    def test_remove_sigma_inverse_pair2(self):
        braid = Braid([3, 1, 2, -2])
        values = braid.remove_sigma_inverse_pair(index=2)._braid
        assert values[0] == 3 and values[1] == 1

    def test_remove_sigma_inverse_pair3(self):
        braid = Braid([-2, 3, 1, 2])
        values = braid.remove_sigma_inverse_pair(index=3)._braid
        assert values[0] == 3 and values[1] == 1

    def test_remove_sigma_inverse_pair4(self):
        braid = Braid([2, 3, 1, -2])
        values = braid.remove_sigma_inverse_pair(index=3)._braid
        assert values[0] == 3 and values[1] == 1

    def test_remove_sigma_inverse_pair5(self):
        braid = Braid([-2, 2, 1, 3])
        values = braid.remove_sigma_inverse_pair(index=0)._braid
        assert values[0] == 1 and values[1] == 3

    def test_remove_sigma_inverse_pair_and_conjugate1(self):
        braid = Braid([4])
        braid = Braid(braid.conjugation(value=1, index=0))
        braid = braid.remove_sigma_inverse_pair(index=0)
        assert braid.values()[1][0] == 4 and braid._braid.shape[0] == 1 