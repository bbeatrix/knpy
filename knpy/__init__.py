import os as _os

from .exceptions import IllegalTransformationException, InvalidBraidException, IndexOutOfRangeException
if _os.environ.get("KNPY_FAST_BRAID", "no").lower() in ["on", "yes", "true", "1"]:
    from .braid_vec import Braid
else:
    from .braid import Braid
