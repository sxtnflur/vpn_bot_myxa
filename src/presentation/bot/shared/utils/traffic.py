GB = 1024 ** 3


def gb_to_bytes(gb: float) -> int:
    return round(gb * GB)


def bytes_to_string(value: int) -> str:
    if value >= GB:
        return f'{value / GB:.2f}'.rstrip('0').rstrip('.') + 'ГБ'
    return f'{value}Б'


def total_gb_to_string(total: int) -> str:
    if total == 0:
        return '♾ Безлимит'
    return bytes_to_string(total)
