from domain.errors import DomainError


class ServiceError(DomainError):
    pass


class NoSubError(ServiceError):
    """
    Вызывает сообщение в боте о необходимости купить подписку для этого действия
    """


class SessionError(ServiceError):
    def __init__(self, status: int, json: dict | None = None, comment: str | None = None):
        self.status = status
        self.json = json
        message = f'SessionError {status}'
        if json:
            message += f' [{json}]'
        if comment:
            message += f': {comment}'
        super().__init__(message)


class IncreaseSubByEmailError(ServiceError):
    pass
