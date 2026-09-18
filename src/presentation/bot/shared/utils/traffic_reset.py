
def traffic_reset_to_string(traffic_reset: str):
    print(f'{traffic_reset=}')
    if traffic_reset == 'never':
        return '♾ Безлимит'
    return ''
