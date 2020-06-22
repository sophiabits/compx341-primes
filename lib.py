from math import sqrt
from itertools import count, islice

def check_prime(n: int) -> bool:
    if n < 2:
        return False

    for number in islice(count(2), int(sqrt(n) - 1)):
        if n % number == 0:
            return False

    return True
