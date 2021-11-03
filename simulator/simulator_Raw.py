

def split_raw_to_word(s: str):
    ll = []
    if len(s) != 300:
        return None
    su = int(s, 16)
    for i in range(1, 11):
        each_word = (su >> (300 - i * 30)) & 0x3fffffff
        ll.append(each_word | 0xc0000000)
    return ll


def get_time_from_raw(s: str):
    if len(s) != 300:
        return None
    return (int(s[7:12], 16) >> 1) & 0x1ffff


