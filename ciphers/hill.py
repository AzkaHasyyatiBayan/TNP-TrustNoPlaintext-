"""
Hill Cipher (26 alphabet characters).
Supports both 2x2 and 3x3 key matrices.
Implements exact integer modular arithmetic for determinant and matrix inverse mod 26.
Non-alphabet characters stripped per Specification 2, padded with 'X' as needed.
"""

import math
import re
from .base import clean_alphabet, mod_inverse

def _matrix_det_2x2(m: list[list[int]]) -> int:
    return (m[0][0] * m[1][1] - m[0][1] * m[1][0])

def _matrix_adj_2x2(m: list[list[int]]) -> list[list[int]]:
    return [
        [m[1][1] % 26, (-m[0][1]) % 26],
        [(-m[1][0]) % 26, m[0][0] % 26]
    ]

def _matrix_det_3x3(m: list[list[int]]) -> int:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )

def _matrix_adj_3x3(m: list[list[int]]) -> list[list[int]]:
    # Cofactor matrix transposed
    cofactors = [
        [
            (m[1][1] * m[2][2] - m[1][2] * m[2][1]),
            -(m[1][0] * m[2][2] - m[1][2] * m[2][0]),
            (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        ],
        [
            -(m[0][1] * m[2][2] - m[0][2] * m[2][1]),
            (m[0][0] * m[2][2] - m[0][2] * m[2][0]),
            -(m[0][0] * m[2][1] - m[0][1] * m[2][0])
        ],
        [
            (m[0][1] * m[1][2] - m[0][2] * m[1][1]),
            -(m[0][0] * m[1][2] - m[0][2] * m[1][0]),
            (m[0][0] * m[1][1] - m[0][1] * m[1][0])
        ]
    ]
    # Transpose cofactors to get adjugate
    adj = [
        [(cofactors[r][c]) % 26 for r in range(3)]
        for c in range(3)
    ]
    return adj

def parse_hill_key(key_input) -> list[list[int]]:
    """
    Parses key into a square matrix of integers mod 26 (2x2 or 3x3).
    Supports:
      - 2D list/tuple
      - Text key of 4 letters (e.g. 'HILL') or 9 letters (e.g. 'GYBNQWERT')
      - Comma/space separated numbers: '3, 2, 5, 7' or '6, 24, 1, 13, 16, 10, 20, 17, 15'
    """
    numbers = []
    if isinstance(key_input, list) and len(key_input) in (2, 3) and isinstance(key_input[0], list):
        return [[int(x) % 26 for x in row] for row in key_input]

    if isinstance(key_input, str):
        # Check if contains letters only
        cleaned = clean_alphabet(key_input)
        num_matches = re.findall(r'-?\d+', key_input)

        if len(num_matches) in (4, 9):
            numbers = [int(n) % 26 for n in num_matches]
        elif len(cleaned) == 4:
            numbers = [(ord(c) - ord('A')) % 26 for c in cleaned]
        elif len(cleaned) == 9:
            numbers = [(ord(c) - ord('A')) % 26 for c in cleaned]
        elif len(cleaned) in (2, 3):
            raise ValueError(f"Hill key text must have 4 letters (for 2x2) or 9 letters (for 3x3), got {len(cleaned)}.")
        else:
            raise ValueError("Hill key must specify a 2x2 matrix (4 elements) or 3x3 matrix (9 elements).")

    dim = 2 if len(numbers) == 4 else 3
    matrix = [numbers[i*dim:(i+1)*dim] for i in range(dim)]
    return matrix

def get_inverse_matrix(matrix: list[list[int]]) -> list[list[int]]:
    """Computes exact modular inverse of 2x2 or 3x3 matrix mod 26."""
    dim = len(matrix)
    if dim == 2:
        det = _matrix_det_2x2(matrix) % 26
        adj = _matrix_adj_2x2(matrix)
    elif dim == 3:
        det = _matrix_det_3x3(matrix) % 26
        adj = _matrix_adj_3x3(matrix)
    else:
        raise ValueError(f"Unsupported Hill matrix dimension: {dim}x{dim}. Only 2x2 and 3x3 are supported.")

    if math.gcd(det, 26) != 1:
        raise ValueError(
            f"Matrix determinant mod 26 is {det}, which has gcd({det}, 26) = {math.gcd(det, 26)} != 1. "
            "Matrix is not invertible mod 26! Please choose an invertible key matrix."
        )

    det_inv = mod_inverse(det, 26)
    inv_matrix = [
        [(adj[r][c] * det_inv) % 26 for c in range(dim)]
        for r in range(dim)
    ]
    return inv_matrix

def encrypt(plaintext: str, key_input) -> str:
    """Encrypts plaintext using Hill Cipher."""
    matrix = parse_hill_key(key_input)
    # Check invertibility upfront so user knows immediately if key is valid for decryption
    _ = get_inverse_matrix(matrix)

    dim = len(matrix)
    clean_p = clean_alphabet(plaintext)
    if not clean_p:
        return ""

    # Pad with 'X' to make length a multiple of dim
    remainder = len(clean_p) % dim
    if remainder != 0:
        clean_p += 'X' * (dim - remainder)

    result = []
    for i in range(0, len(clean_p), dim):
        block = [(ord(clean_p[i + j]) - ord('A')) for j in range(dim)]
        # Multiply matrix * block
        for r in range(dim):
            c_val = sum(matrix[r][c] * block[c] for c in range(dim)) % 26
            result.append(chr(c_val + ord('A')))

    return "".join(result)

def decrypt(ciphertext: str, key_input) -> str:
    """Decrypts ciphertext using Hill Cipher."""
    matrix = parse_hill_key(key_input)
    inv_matrix = get_inverse_matrix(matrix)
    dim = len(matrix)

    clean_c = clean_alphabet(ciphertext)
    if not clean_c:
        return ""
    if len(clean_c) % dim != 0:
        raise ValueError(f"Ciphertext length ({len(clean_c)}) must be a multiple of matrix dimension ({dim}).")

    result = []
    for i in range(0, len(clean_c), dim):
        block = [(ord(clean_c[i + j]) - ord('A')) for j in range(dim)]
        # Multiply inv_matrix * block
        for r in range(dim):
            p_val = sum(inv_matrix[r][c] * block[c] for c in range(dim)) % 26
            result.append(chr(p_val + ord('A')))

    return "".join(result)
