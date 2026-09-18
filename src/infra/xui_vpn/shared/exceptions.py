class XuiApiError(Exception):
    """Raised when a 3x-ui API call responds with success: false."""

    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)


class ClientAlreadyExistsError(XuiApiError):
    """Raised by AddClient when the panel already has a client with this email."""
