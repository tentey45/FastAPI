class TodoNotFoundError(Exception):
    """Raised when a requested todo item does not exist."""

    def __init__(self, message: str = "Todo not found") -> None:
        super().__init__(message)
        self.message = message


class FolderNotFoundError(Exception):
    """Raised when a requested folder does not exist."""

    def __init__(self, message: str = "Folder not found") -> None:
        super().__init__(message)
        self.message = message


class ChecklistItemNotFoundError(Exception):
    """Raised when a requested checklist item does not exist."""

    def __init__(self, message: str = "Checklist item not found") -> None:
        super().__init__(message)
        self.message = message

