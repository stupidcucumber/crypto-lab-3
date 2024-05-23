from cryptography.hazmat.primitives.asymmetric import rsa


def generate_prime(n_bits):
    prime_number = utils.generate_primes(n_bits, 1)[0]
    return prime_number