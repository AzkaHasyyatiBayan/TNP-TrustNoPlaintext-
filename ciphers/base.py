"""
Cryptographic Base Utilities
Provides text cleansing (A-Z filtering), modular arithmetic,
Base64 formatting, and hex inspection helpers.
"""

import base64
import math
import re

def clean_alphabet(text: str) -> str:
    """
    Cleanses text according to Specification 2:
    Only keep alphabetic characters A-Z, converted to uppercase.
    Spaces, digits, and punctuation are completely removed.
    """
    if not text:
        return ""
    # Filter only [A-Za-z] and convert to UPPERCASE
    return re.sub(r'[^A-Za-z]', '', text).upper()

def egcd(a: int, b: int):
    """Extended Euclidean Algorithm returns (g, x, y) such that a*x + b*y = g = gcd(a, b)"""
    if a == 0:
        return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y

def mod_inverse(a: int, m: int = 26):
    """
    Returns modular inverse of a mod m.
    Raises ValueError if gcd(a, m) != 1.
    """
    a = a % m
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError(f"No modular inverse for {a} modulo {m} (gcd is {g}).")
    return (x % m + m) % m

def to_base64_no_spaces(data: bytes, lowercase: bool = False, uppercase: bool = False) -> str:
    """
    Specification 4 & 5:
    Displays messages in Base64 without spaces, in either all lowercase or all uppercase (or standard).
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    b64 = base64.b64encode(data).decode('ascii').replace('\n', '').replace('\r', '').replace(' ', '')
    if lowercase:
        return b64.lower()
    if uppercase:
        return b64.upper()
    return b64

def from_base64(b64_str: str) -> bytes:
    """Decodes Base64 string back to raw bytes."""
    clean_b64 = re.sub(r'\s+', '', b64_str)
    # Add padding if needed
    missing_padding = len(clean_b64) % 4
    if missing_padding:
        clean_b64 += '=' * (4 - missing_padding)
    return base64.b64decode(clean_b64)

def format_hex_dump(data_bytes: bytes, max_bytes: int = 512) -> list:
    """
    Generates a structured hex dump like aes.online-domain-tools.com
    Returns a list of dicts: [{'offset': '00000000', 'hex': '46 4f ...', 'ascii': 'FO...'}, ...]
    """
    lines = []
    sample = data_bytes[:max_bytes]
    for i in range(0, len(sample), 16):
        chunk = sample[i:i + 16]
        offset = f"{i:08x}"
        hex_bytes = " ".join(f"{b:02x}" for b in chunk)
        # Pad hex string if chunk < 16
        if len(chunk) < 16:
            hex_bytes = hex_bytes.ljust(16 * 3 - 1)
        ascii_repr = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append({
            "offset": offset,
            "hex": hex_bytes,
            "ascii": ascii_repr
        })
    return lines
