import logging

from typing_extensions import Literal


def config_logger(level: Literal['DEBUG', 'INFO', 'WARN', 'ERROR']):
    if level not in ('DEBUG', 'INFO', 'WARN', 'ERROR'):
        raise ValueError('Wrong logging level: ', level)

    level = getattr(logging, level)

    logging.basicConfig(
        level=level,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
        force=True
    )

    logging.info(f'Установлен уровень логов: {logging.getLevelName(level)}')
