"""
Custom Binary Container (.dat) for Secure File Packaging (Specifications 8 & 9).
Preserves original file name, extension, MIME type, and cryptographic checksum.
Enables automatic restoration of the original file format upon decryption.
"""

import json
import struct
import hashlib
from datetime import datetime, timezone

MAGIC_HEADER = b'TNP1'
CONTAINER_VERSION = 1

def pack_container(
    encrypted_payload: bytes,
    original_name: str,
    cipher_name: str,
    original_sha256: str,
    original_size: int,
    mime_type: str = "application/octet-stream"
) -> bytes:
    """
    Packs encrypted payload with metadata into a .dat container.
    Structure:
      [4B: MAGIC b'KRYP']
      [1B: Version]
      [4B: uint32 BigEndian Metadata Length]
      [NB: JSON Metadata UTF-8]
      [Remaining: Encrypted Payload Bytes]
    """
    ext = ""
    if "." in original_name:
        ext = "." + original_name.rsplit(".", 1)[-1].lower()

    metadata = {
        "v": CONTAINER_VERSION,
        "name": original_name,
        "ext": ext,
        "mime": mime_type,
        "cipher": cipher_name,
        "size": original_size,
        "sha256": original_sha256,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    meta_bytes = json.dumps(metadata, separators=(',', ':')).encode('utf-8')
    header_length = len(meta_bytes)

    packet = bytearray()
    packet.extend(MAGIC_HEADER)
    packet.append(CONTAINER_VERSION)
    packet.extend(struct.pack('>I', header_length))
    packet.extend(meta_bytes)
    packet.extend(encrypted_payload)
    return bytes(packet)

def is_krypto_container(data: bytes) -> bool:
    """Checks if raw data begins with KRYP container magic header."""
    return len(data) >= 9 and data[:4] == MAGIC_HEADER

def unpack_container(data: bytes) -> tuple[dict, bytes]:
    """
    Unpacks .dat container, extracting metadata and raw encrypted payload.
    Raises ValueError if data is not a valid container.
    """
    if not is_krypto_container(data):
        raise ValueError("File is not a valid TNP (Trust No Plaintext) .dat encrypted container.")

    version = data[4]
    header_len = struct.unpack('>I', data[5:9])[0]
    meta_end = 9 + header_len

    if len(data) < meta_end:
        raise ValueError("Corrupt file container: header length exceeds file size.")

    meta_bytes = data[9:meta_end]
    payload_bytes = data[meta_end:]

    try:
        metadata = json.loads(meta_bytes.decode('utf-8'))
    except Exception as e:
        raise ValueError(f"Corrupt container metadata: {str(e)}")

    return metadata, payload_bytes
