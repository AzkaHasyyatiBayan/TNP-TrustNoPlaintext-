"""
Affine Cipher (26 alphabet characters).
Formula:
    C_i = (a * P_i + b) mod 26
    P_i = a^(-1) * (C_i - b) mod 26
Requirement:
    gcd(a, 26) == 1
"""

import re
import math
from .base import clean_alphabet, mod_inverse

VALID_A_VALUES = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]

def parse_affine_key(key_input) -> tuple[int, int]:
    """
    Parses key into (a, b) tuple.
    Accepts:
      - tuple or list of 2 ints: (7, 10)
      - string format: "7, 10", "7,10", "a=7, b=10", "7 10"
    """
    if isinstance(key_input, (tuple, list)) and len(key_input) >= 2:
        a = int(key_input[0])
        b = int(key_input[1])
    elif isinstance(key_input, str):
        # Extract numbers using regex
        numbers = [int(n) for n in re.findall(r'-?\d+', key_input)]
        if len(numbers) >= 2:
            a, b = numbers[0], numbers[1]
        else:
            raise ValueError("Affine key must provide both 'a' (slope) and 'b' (intercept), e.g. '7, 10'.")
    elif isinstance(key_input, dict):
        a = int(key_input.get('a', 1))
        b = int(key_input.get('b', 0))
    else:
        raise ValueError("Invalid Affine key format.")

    a_mod = a % 26
    if math.gcd(a_mod, 26) != 1:
        raise ValueError(
            f"Value 'a'={a} (mod 26 = {a_mod}) is invalid because gcd({a_mod}, 26) = {math.gcd(a_mod, 26)} != 1. "
            f"Allowed values for 'a': {VALID_A_VALUES}"
        )
    return a_mod, b % 26

def encrypt(plaintext: str, key_input) -> str:
    """Encrypts plaintext using Affine Cipher."""
    a, b = parse_affine_key(key_input)
    clean_p = clean_alphabet(plaintext)
    if not clean_p:
        return ""

    result = []
    for char in clean_p:
        p_val = ord(char) - ord('A')
        c_val = (a * p_val + b) % 26
        result.append(chr(c_val + ord('A')))
    return "".join(result)

def decrypt(ciphertext: str, key_input) -> str:
    """Decrypts ciphertext using Affine Cipher."""
    a, b = parse_affine_key(key_input)
    clean_c = clean_alphabet(ciphertext)
    if not clean_c:
        return ""

    a_inv = mod_inverse(a, 26)
    result = []
    for char in clean_c:
        c_val = ord(char) - ord('A')
        p_val = (a_inv * (c_val - b)) % 26
        result.append(chr(p_val + ord('A')))
    return "".join(result)
