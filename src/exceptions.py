class BaseException(Exception):
    """
    Base class for custom Database Exceptions
    """
    pass

class SessionException(BaseException):
    def __init__(self, exception: str, message: str = "error in database session"):
        super().__init__()
        self.exception = exception
        self.message: str = message
    def __str__(self):
        return f"{self.message}: {self.exception}"
        
class ManagerException(BaseException):
    def __init__(self, name: str, exception: str, message: str = "error in manager"):
        super().__init__()
        self.exception = exception
        self.message: str = message
        self.name: str = name
    def __str__(self) -> str:
        return f"{self.message}:<{self.name}> {self.exception}"