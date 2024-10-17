class IllegalTransformationException(Exception):
    """
    Exception raised for errors in the transformation process that are deemed illegal.
    
    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message="Illegal transformation attempted"):
        self.message = message
        super().__init__(f"{self.message}")