"""
Extended Vigenere Cipher (256 ASCII characters / raw bytes 0-255).
Operates directly on bytes, supporting arbitrary binary files (images, audio, video, database)
as well as raw text.
Formula:
    C_i = (P_i + K_i) mod 256
    P_i = (C_i - K_i + 256) mod 256
"""

def _ensure_bytes(val) -> bytes:
    if isinstance(val, str):
        return val.encode('utf-8')
    elif isinstance(val, (bytes, bytearray)):
        return bytes(val)
    else:
        raise TypeError("Input data must be str or bytes.")

def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    """Encrypts raw byte array using Extended Vigenere (mod 256)."""
    data = _ensure_bytes(data)
    key = _ensure_bytes(key)
    if not key:
        raise ValueError("Key cannot be empty.")
    if not data:
        return b""

    k_len = len(key)
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = (data[i] + key[i % k_len]) % 256
    return bytes(result)

def decrypt_bytes(data: bytes, key: bytes) -> bytes:
    """Decrypts raw byte array using Extended Vigenere (mod 256)."""
    data = _ensure_bytes(data)
    key = _ensure_bytes(key)
    if not key:
        raise ValueError("Key cannot be empty.")
    if not data:
        return b""

    k_len = len(key)
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = (data[i] - key[i % k_len] + 256) % 256
    return bytes(result)

def encrypt(text: str, key: str) -> bytes:
    """Wrapper for text input returning encrypted bytes."""
    return encrypt_bytes(text.encode('utf-8'), key.encode('utf-8'))

def decrypt(data: bytes, key: str) -> bytes:
    """Wrapper for decrypting bytes returning decrypted bytes."""
    return decrypt_bytes(data, key.encode('utf-8'))
