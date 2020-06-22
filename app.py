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
    # retries = 5
    # while True:
    #     try:
    #         return cache.set(number, True)
    #     except redis.exceptions.ConnectionError as exc:
    #         if retries == 0:
    #             raise exc
    #         retries -= 1
    #         time.sleep(0.5)

# def get_hit_count():
#     retries = 5
#     while True:
#         try:
#             return cache.incr('hits')
#         except redis.exceptions.ConnectionError as exc:
#             if retries == 0:
#                 raise exc
#             retries -= 1
#             time.sleep(0.5)


# @app.route('/')
# def hello():
#     count = get_hit_count()
#     return 'Hello World! I have been seen {} times.\n'.format(count)

@app.route('/isPrime/<int:number>', methods=['GET'])
def is_prime(number):
    if check_prime(number):
        print(f'Storing {number} into Redis...', file=sys.stderr)
        store_prime(number)
        return f'{number} is prime'
    else:
        return f'{number} is not prime'

@app.route('/primesStored', methods=['GET'])
def primes_stored():
    primes = get_stored_primes()
    print(primes, file=sys.stderr)
    return json.dumps(primes)
