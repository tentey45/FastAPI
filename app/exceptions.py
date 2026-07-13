class TodoNotFoundError(Exception):
    """Raised when a requested todo item does not exist."""

    def __init__(self, message: str = "Todo not found") -> None:
        super().__init__(message)
        self.message = message
