class IllegalTransformationException(Exception):
    """
    Exception raised for errors in the transformation process that are deemed illegal.
    
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message="Illegal transformation attempted"):
        self.message = message
        super().__init__(f"{self.message}")

class InvalidBraidException(Exception):
    """
    Exception raised for giving invalid braid in Braid class init.
    
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message="Invalid braid, should not contain zero"):
        self.message = message
        super().__init__(f"{self.message}")

class IndexOutOfRangeException(Exception):
    """
    Exception raised for giving invalid braid in Braid class init.
    
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message="Index is out of range"):
        self.message = message
        super().__init__(f"{self.message}")