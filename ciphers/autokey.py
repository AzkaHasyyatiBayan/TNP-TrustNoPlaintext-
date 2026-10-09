"""
Auto-Key Vigenere Cipher (26 alphabet characters).
Keystream is formed by concatenating the initial user key followed by the plaintext.
Decryption progressively recovers the keystream from decrypted plaintext characters.
"""

from .base import clean_alphabet

def encrypt(plaintext: str, key: str) -> str:
    """
    Encrypts plaintext using Auto-Key Vigenere cipher mod 26.
    Keystream = Key + Plaintext[:N - len(Key)]
    C_i = (P_i + Keystream_i) mod 26
    """
    clean_p = clean_alphabet(plaintext)
    clean_k = clean_alphabet(key)
    if not clean_k:
        raise ValueError("Key cannot be empty and must contain at least one alphabetic character.")
    if not clean_p:
        return ""

    keystream_chars = list(clean_k) + list(clean_p)
    result = []
    for i, p_char in enumerate(clean_p):
        p_val = ord(p_char) - ord('A')
        k_val = ord(keystream_chars[i]) - ord('A')
        c_val = (p_val + k_val) % 26
        result.append(chr(c_val + ord('A')))
    return "".join(result)

def decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypts ciphertext using Auto-Key Vigenere cipher mod 26.
    Dynamically rebuilds the keystream from recovered plaintext characters.
    P_i = (C_i - Keystream_i + 26) mod 26
    """
    clean_c = clean_alphabet(ciphertext)
    clean_k = clean_alphabet(key)
    if not clean_k:
        raise ValueError("Key cannot be empty and must contain at least one alphabetic character.")
    if not clean_c:
        return ""

    recovered_p = []
    k_list = list(clean_k)
    k_len = len(k_list)

    for i, c_char in enumerate(clean_c):
        if i < k_len:
            k_char = k_list[i]
        else:
            k_char = recovered_p[i - k_len]

        c_val = ord(c_char) - ord('A')
        k_val = ord(k_char) - ord('A')
        p_val = (c_val - k_val + 26) % 26
        recovered_p.append(chr(p_val + ord('A')))

    return "".join(recovered_p)
