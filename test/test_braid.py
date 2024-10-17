import pytest
from ..knpy.braid import Braid
from ..knpy.illegal_transformation_exception import IllegalTransformationException

class TestBraidClassBraidRelations:
    def test_stabilization(self):
        braid = Braid([1, -2, 3])
        braid.stabilization()
        self.assertEqual(braid.values()[0], 5)
        self.assertEqual(braid.values()[1][-1], 3)
        self.assertEqual(len(braid.values()[1]), 4)

    def test_destabilization(self):
        braid = Braid([1, -2, 3])
        braid.destabilization()
        self.assertEqual(braid.values()[0], 3)
        self.assertEqual(len(braid.values()[1]), 2)

    def test_destabilization_exception(self):
        braid = Braid([-3 ,1, -2, 3])
        with self.assertRaises(IllegalTransformationException):
            braid.destabilization()