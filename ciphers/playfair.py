"""
Playfair Cipher (26 alphabet characters mapped to 5x5 matrix).
Letter 'J' is merged into 'I'.
Pairs of identical characters are split with 'X' (or 'Z' if 'X').
Odd length text is padded with 'X' (or 'Z' if 'X').
Includes helper to inspect the generated 5x5 matrix.
"""

from .base import clean_alphabet

def generate_playfair_matrix(key: str) -> tuple[list[list[str]], dict[str, tuple[int, int]]]:
    """
    Generates 5x5 Playfair matrix and a coordinate lookup dict.
    'J' is replaced with 'I'.
    """
    clean_k = clean_alphabet(key).replace('J', 'I')
    used = set()
    matrix_letters = []

    for char in clean_k:
        if char not in used and char in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
            used.add(char)
            matrix_letters.append(char)

    for char in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if char not in used:
            used.add(char)
            matrix_letters.append(char)

    matrix = [matrix_letters[i*5:(i+1)*5] for i in range(5)]
    coords = {}
    for r in range(5):
        for c in range(5):
            coords[matrix[r][c]] = (r, c)

    return matrix, coords

def prepare_playfair_plaintext(text: str) -> list[tuple[str, str]]:
    """
    Cleans text, replaces 'J' with 'I', splits duplicates with 'X' / 'Z',
    and pads odd-length text.
    """
    clean_p = clean_alphabet(text).replace('J', 'I')
    if not clean_p:
        return []

    digraphs = []
    i = 0
    while i < len(clean_p):
        first = clean_p[i]
        if i + 1 < len(clean_p):
            second = clean_p[i + 1]
            if first == second:
                # Same letter, insert filler
                filler = 'Z' if first == 'X' else 'X'
                digraphs.append((first, filler))
                i += 1
            else:
                digraphs.append((first, second))
                i += 2
        else:
            # Lone character at the end
            filler = 'Z' if first == 'X' else 'X'
            digraphs.append((first, filler))
            i += 1

    return digraphs

def encrypt(plaintext: str, key: str) -> str:
    """Encrypts plaintext using Playfair Cipher."""
    clean_k = clean_alphabet(key)
    if not clean_k:
        raise ValueError("Key cannot be empty.")

    matrix, coords = generate_playfair_matrix(clean_k)
    digraphs = prepare_playfair_plaintext(plaintext)
    if not digraphs:
        return ""

    result = []
    for c1, c2 in digraphs:
        r1, col1 = coords[c1]
        r2, col2 = coords[c2]

        if r1 == r2:
            # Same row -> shift right
            result.append(matrix[r1][(col1 + 1) % 5])
            result.append(matrix[r2][(col2 + 1) % 5])
        elif col1 == col2:
            # Same column -> shift down
            result.append(matrix[(r1 + 1) % 5][col1])
            result.append(matrix[(r2 + 1) % 5][col2])
        else:
            # Rectangle -> swap columns
            result.append(matrix[r1][col2])
            result.append(matrix[r2][col1])

    return "".join(result)

def decrypt(ciphertext: str, key: str) -> str:
    """Decrypts ciphertext using Playfair Cipher."""
    clean_k = clean_alphabet(key)
    if not clean_k:
        raise ValueError("Key cannot be empty.")

    matrix, coords = generate_playfair_matrix(clean_k)
    clean_c = clean_alphabet(ciphertext).replace('J', 'I')
    if not clean_c:
        return ""
    if len(clean_c) % 2 != 0:
        raise ValueError("Ciphertext length must be even for Playfair decryption.")

    result = []
    for i in range(0, len(clean_c), 2):
        c1, c2 = clean_c[i], clean_c[i + 1]
        r1, col1 = coords[c1]
        r2, col2 = coords[c2]

        if r1 == r2:
            # Same row -> shift left
            result.append(matrix[r1][(col1 - 1 + 5) % 5])
            result.append(matrix[r2][(col2 - 1 + 5) % 5])
        elif col1 == col2:
            # Same column -> shift up
            result.append(matrix[(r1 - 1 + 5) % 5][col1])
            result.append(matrix[(r2 - 1 + 5) % 5][col2])
        else:
            # Rectangle -> swap columns
            result.append(matrix[r1][col2])
            result.append(matrix[r2][col1])

    return "".join(result)
