"""
本模块用于将微博博文的ID和其base62编码的ID进行转换.
This module can be applied to convert between ID and base62-coded ID of
Weibo statuses.

Source & Thanks:
[mrluanma/base62.py](https://gist.github.com/mrluanma/6000424)
"""

import sys


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def rsplit(s, count):
    f = lambda x: x > 0 and x or 0
    return [s[f(i - count):i] for i in range(len(s), 0, -count)]

def id2bid(mid):
    result = ''
    for i in rsplit(mid, 7):
        str62 = base62_encode(int(i))
        result = str62.zfill(4) + result
    return result.lstrip('0')

def bid2id(input):
    result = ''
    for i in rsplit(input, 4):
        str10 = str(base62_decode(i)).zfill(7)
        result = str10 + result
    return result.lstrip('0')

def base62_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X

    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1
    return num

def test():
    assert id2bid('231101124784859058') == 'Bh0tgako3U'
    assert bid2id('Bh0tgako3U') == '231101124784859058'

    assert id2bid('3491273850170657') == 'yCirT0Iox'
    assert bid2id('yCirT0Iox') == '3491273850170657'

    print(bid2id('H67N8hxyN'))


if __name__ == '__main__':
    test()
