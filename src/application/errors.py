from domain.errors import DomainError


class ServiceError(DomainError):
    pass


class NoSubError(ServiceError):
    """
    Вызывает сообщение в боте о необходимости купить подписку для этого действия
    """
