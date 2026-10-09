"""
Super Enkripsi: Gabungan Extended Vigenere Cipher (256 ASCII / Full Byte 0-255)
dan Cipher Transposisi Metode Kolom (Columnar Transposition).
Operates directly on bytes, supporting arbitrary files (images, audio, video, database)
and text strings without data loss.
"""

from . import extended_vigenere

def _get_column_order(trans_key: str) -> list[int]:
    """
    Returns the permutation order of columns based on alphabetical sort of the key.
    Ties broken by original index.
    Example: 'ZEBRA' -> sorted is A(4), B(2), E(1), R(3), Z(0) -> [4, 2, 1, 3, 0]
    """
    if not trans_key:
        raise ValueError("Transposition key cannot be empty.")
    # Pair character with original index
    indexed = [(char, i) for i, char in enumerate(trans_key)]
    # Sort primarily by character, secondarily by index
    sorted_indexed = sorted(indexed, key=lambda x: (x[0], x[1]))
    # Return list of original column indices in sorted order
    return [item[1] for item in sorted_indexed]

def columnar_transposition_encrypt(data: bytes, trans_key: str) -> bytes:
    """
    Irregular columnar transposition on bytes (no padding required, exact length preserved).
    """
    if not data or not trans_key:
        return data

    col_order = _get_column_order(trans_key)
    num_cols = len(trans_key)
    num_bytes = len(data)

    # Base rows per column
    base_rows = num_bytes // num_cols
    extra = num_bytes % num_cols

    # Heights of each column (0 .. num_cols-1)
    col_heights = [base_rows + (1 if c < extra else 0) for c in range(num_cols)]

    # Read data row-by-row into columns
    columns = [bytearray() for _ in range(num_cols)]
    for i, b in enumerate(data):
        col_idx = i % num_cols
        columns[col_idx].append(b)

    # Read out columns in the order defined by trans_key
    result = bytearray()
    for col_idx in col_order:
        result.extend(columns[col_idx])

    return bytes(result)

def columnar_transposition_decrypt(data: bytes, trans_key: str) -> bytes:
    """
    Reverses irregular columnar transposition on bytes.
    """
    if not data or not trans_key:
        return data

    col_order = _get_column_order(trans_key)
    num_cols = len(trans_key)
    num_bytes = len(data)

    base_rows = num_bytes // num_cols
    extra = num_bytes % num_cols
    col_heights = [base_rows + (1 if c < extra else 0) for c in range(num_cols)]

    # Reconstruct columns from transposed stream
    columns = [None] * num_cols
    ptr = 0
    for col_idx in col_order:
        height = col_heights[col_idx]
        columns[col_idx] = data[ptr:ptr + height]
        ptr += height

    # Read back row-by-row
    result = bytearray(num_bytes)
    col_ptrs = [0] * num_cols
    for i in range(num_bytes):
        col_idx = i % num_cols
        result[i] = columns[col_idx][col_ptrs[col_idx]]
        col_ptrs[col_idx] += 1

    return bytes(result)

def encrypt(data: bytes, vigenere_key: str, trans_key: str) -> bytes:
    """
    Super Encryption:
    Step 1: Extended Vigenere Encryption (mod 256)
    Step 2: Columnar Transposition
    """
    if not vigenere_key or not trans_key:
        raise ValueError("Both Vigenere key and Transposition key are required for Super Encryption.")

    # 1. Extended Vigenere
    v_enc = extended_vigenere.encrypt_bytes(data, vigenere_key.encode('utf-8'))
    # 2. Columnar Transposition
    super_enc = columnar_transposition_encrypt(v_enc, trans_key)
    return super_enc

def decrypt(data: bytes, vigenere_key: str, trans_key: str) -> bytes:
    """
    Super Decryption:
    Step 1: Reverse Columnar Transposition
    Step 2: Extended Vigenere Decryption (mod 256)
    """
    if not vigenere_key or not trans_key:
        raise ValueError("Both Vigenere key and Transposition key are required for Super Encryption.")

    # 1. Reverse Transposition
    v_enc = columnar_transposition_decrypt(data, trans_key)
    # 2. Reverse Extended Vigenere
    decrypted = extended_vigenere.decrypt_bytes(v_enc, vigenere_key.encode('utf-8'))
    return decrypted
