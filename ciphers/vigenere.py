"""
Standard Vigenere Cipher (26 alphabet characters).
Applies modular addition mod 26.
Non-alphabet characters are stripped per Specification 2.
"""

from .base import clean_alphabet

def encrypt(plaintext: str, key: str) -> str:
    """
    Encrypts plaintext using standard Vigenere cipher mod 26.
    C_i = (P_i + K_i) mod 26
    """
    clean_p = clean_alphabet(plaintext)
    clean_k = clean_alphabet(key)
    if not clean_k:
        raise ValueError("Key cannot be empty and must contain at least one alphabetic character.")
    if not clean_p:
        return ""

    result = []
    k_len = len(clean_k)
    for i, char in enumerate(clean_p):
        p_val = ord(char) - ord('A')
        k_val = ord(clean_k[i % k_len]) - ord('A')
        c_val = (p_val + k_val) % 26
        result.append(chr(c_val + ord('A')))
    return "".join(result)

def decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypts ciphertext using standard Vigenere cipher mod 26.
    P_i = (C_i - K_i + 26) mod 26
    """
    clean_c = clean_alphabet(ciphertext)
    clean_k = clean_alphabet(key)
    if not clean_k:
        raise ValueError("Key cannot be empty and must contain at least one alphabetic character.")
    if not clean_c:
        return ""

    result = []
    k_len = len(clean_k)
    for i, char in enumerate(clean_c):
        c_val = ord(char) - ord('A')
        k_val = ord(clean_k[i % k_len]) - ord('A')
        p_val = (c_val - k_val + 26) % 26
        result.append(chr(p_val + ord('A')))
    return "".join(result)
