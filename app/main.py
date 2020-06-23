import json
import sys
import time
import typing

import backoff
import redis
from flask import Flask

from .lib import check_prime

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

KEY_PREFIX = 'primes:'

@backoff.on_exception(
    backoff.expo,
    redis.exceptions.ConnectionError,
    max_tries=5,
)
def get_stored_primes() -> typing.List[int]:
    primes = []

    for key in cache.scan_iter(f'{KEY_PREFIX}*'):
        key = key.decode('utf-8')
        print(key, file=sys.stderr)
        if key.startswith(KEY_PREFIX):
            key_without_prefix = key[len(KEY_PREFIX):] # 'prime:3' -> '3'
            primes.append(int(key_without_prefix))

    return primes


@backoff.on_exception(
    backoff.expo,
    redis.exceptions.ConnectionError,
    max_tries=5,
)
def store_prime(number: int):
    cache.set(f'{KEY_PREFIX}{number}', '')

@app.route('/isPrime/<int:number>', methods=['GET'])
def is_prime(number):
    if check_prime(number):
        store_prime(number)
        return f'{number} is prime'
    else:
        return f'{number} is not prime'

@app.route('/primesStored', methods=['GET'])
def primes_stored():
    primes = get_stored_primes()
    return json.dumps(primes)
