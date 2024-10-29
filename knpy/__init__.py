import os as _os
from . import braid, braid_vec

Braid: type['braid.Braid'] | type['braid_vec.Braid']
from .exceptions import IllegalTransformationException, InvalidBraidException, IndexOutOfRangeException
if _os.environ.get("KNPY_FAST_BRAID", default="no").lower() in ["on", "yes", "true", "1"]:
    from .braid_vec import Braid
else:
    from .braid import Braid
