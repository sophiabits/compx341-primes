import app.main
from app.lib import check_prime

primes = frozenset([
    2, # boundary
    3,
    5,
    7,
    11,
    79,

    # selection of numbers from: https://primes.utm.edu/lists/small/10000.txt
    100741,
    101653,
    104707,
    104729,

    # a few large primes from: https://primes.utm.edu/lists/small/millions/
    982448321,
    982449731,
    982451111,
    982451653,
])

nonprimes = frozenset([
    -2563,
    -5, # negatives are always non-prime
    0,
    1, # boundary
    48,
    63,
    1729,
])


def test_check_prime():
    for num in primes:
        assert check_prime(num) is True

    for num in nonprimes:
        assert check_prime(num) is False


def test_is_prime(mocker):
    mocker.patch('app.main.store_prime')
    api = app.main.app.test_client()

    for num in nonprimes:
        if num < 0:
            # flask doesn't parse negative numbers in the route correctly -- skip
            continue

        response = api.get(f'/isPrime/{num}')

        assert b'is not prime' in response.data

        # ensure we _don't_ store this number as a prime
        assert not app.main.store_prime.called

    for num in primes:
        app.main.store_prime.reset_mock()
        response = api.get(f'/isPrime/{num}')

        assert b'is prime' in response.data

        # make sure that store_prime gets called
        app.main.store_prime.assert_called_once_with(num)


def test_stored_primes(mocker):
    mocker.patch('app.main.get_stored_primes')
    app.main.get_stored_primes.return_value = [1, 3, 5]

    api = app.main.app.test_client()
    response = api.get('/primesStored')

    assert response.data == b'[1, 3, 5]'
