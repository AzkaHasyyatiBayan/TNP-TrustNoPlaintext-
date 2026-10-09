"""
End-to-End API and File Processing Integration Test.
Tests all HTTP endpoints, text ciphers, and binary file vault operations
against the running Flask server (http://127.0.0.1:5000).
"""

import urllib.request
import urllib.parse
import json
import hashlib
import os
import sys

BASE_URL = "http://127.0.0.1:5000"
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_data")

def test_get(url):
    req = urllib.request.Request(f"{BASE_URL}{url}")
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read()

def test_post_json(url, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}{url}",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def test_post_multipart(url, file_path, fields):
    boundary = "----WebKitFormBoundarySentinel7MA4YWxkTrZu0gW"
    body = bytearray()

    for k, v in fields.items():
        body.extend(f"--{boundary}\r\n".encode('ascii'))
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode('ascii'))
        body.extend(f"{v}\r\n".encode('utf-8'))

    # Add file
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    body.extend(f"--{boundary}\r\n".encode('ascii'))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode('ascii'))
    body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
    body.extend(file_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode('ascii'))

    req = urllib.request.Request(
        f"{BASE_URL}{url}",
        data=bytes(body),
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def run_all_e2e_tests():
    print("=== STARTING KRYPTO-SENTINEL E2E INTEGRATION SUITE ===")

    # 1. Test Home Page
    print("\n[1] Testing GET / (Main Dashboard SPA)...")
    status, html_bytes = test_get("/")
    assert status == 200, f"Expected 200, got {status}"
    assert b"TNP" in html_bytes
    assert b"Text Studio" in html_bytes
    assert b"Binary File Vault" in html_bytes
    print(" -> [PASS] Home Page rendered successfully with brand and tabs.")

    # 2. Test Ciphers Metadata
    print("\n[2] Testing GET /api/ciphers...")
    status, ciphers_data = test_post_json("/api/ciphers", {}) if False else (200, json.loads(test_get("/api/ciphers")[1].decode('utf-8')))
    assert ciphers_data["success"] is True
    assert len(ciphers_data["ciphers"]) == 8
    print(" -> [PASS] All 8 cryptographic algorithms returned in metadata.")

    # 3. Test Text Ciphers (Encrypt & Decrypt)
    text_samples = [
        ("vigenere_standard", {"key": "SECRETKEY"}, "DI BAWAH SINAR BULAN PURNAMA"),
        ("vigenere_autokey", {"key": "SENTINEL"}, "NEGARA PENGHASIL MINYAK BUMI TERBESAR"),
        ("extended_vigenere", {"key": "AegisPass2026"}, "Pesan rahasia 123!@# with full ASCII characters."),
        ("playfair", {"key": "MONARCHY"}, "TEMUKAN SAYA DI JALAN SUDIRMAN PUKUL SEPULUH"),
        ("affine", {"key_a": 7, "key_b": 10}, "KRIPTOGRAFI KLASIK DAN MODERN"),
        ("hill", {"key": "3, 2, 5, 7"}, "PAY MORE MONEY PLEASE"),
        ("super_encryption", {"vigenere_key": "SENTINEL", "trans_key": "TACTICAL"}, "SUPER SECRET PAYLOAD TRANSPOSED"),
        ("enigma", {"rotors": "I, II, III", "reflector": "B", "rings": "1, 1, 1", "positions": "ABC", "plugboard": "AB CD EF"}, "HELLOWORLDFROMENIGMA")
    ]

    print("\n[3] Testing Text Processing for all 8 ciphers...")
    for cipher_id, params, sample_text in text_samples:
        payload_enc = {
            "cipher": cipher_id,
            "operation": "encrypt",
            "text": sample_text,
            "case_mode": "upper",
            **params
        }
        status, res_enc = test_post_json("/api/process/text", payload_enc)
        assert res_enc["success"] is True, f"Failed enc {cipher_id}: {res_enc}"
        assert res_enc["base64_output"] != ""
        assert " " not in res_enc["base64_output"]  # Spek 5: tanpa spasi

        # Decrypt
        payload_dec = {
            "cipher": cipher_id,
            "operation": "decrypt",
            "text": res_enc["output_text"],
            "case_mode": "upper",
            **params
        }
        status, res_dec = test_post_json("/api/process/text", payload_dec)
        assert res_dec["success"] is True, f"Failed dec {cipher_id}: {res_dec}"
        print(f" -> [PASS] {cipher_id.upper()}: Encrypted & Decrypted ({res_enc['duration_ms']}ms, B64 len: {len(res_enc['base64_output'])})")

    # 4. Test Binary File Vault with All 5 Synthetic Files
    print("\n[4] Testing Binary File Vault (.dat packaging & restoration) on all 5 files...")
    sample_files = [
        "confidential_defense_memo.txt",
        "satellite_recon_target.jpg",
        "defense_payroll_ledger.db",
        "tactical_radio_intercept.wav",
        "surveillance_cctv_feed.mp4"
    ]

    for filename in sample_files:
        filepath = os.path.join(SAMPLE_DIR, filename)
        with open(filepath, "rb") as f:
            orig_bytes = f.read()
        orig_sha256 = hashlib.sha256(orig_bytes).hexdigest()

        # Encrypt file to .dat container using Super Enkripsi
        enc_fields = {
            "cipher": "super_encryption",
            "operation": "encrypt",
            "vigenere_key": "SENTINELKEY2026",
            "trans_key": "TACTICAL"
        }
        status, enc_res = test_post_multipart("/api/process/file", filepath, enc_fields)
        assert enc_res["success"] is True
        assert enc_res["download_filename"].endswith(".dat")
        dl_url = enc_res["download_url"]

        # Download the encrypted .dat file
        status, dat_bytes = test_get(dl_url)
        assert status == 200
        assert dat_bytes[:4] == b"TNP1"  # Magic header verification

        # Save temporary .dat file
        temp_dat_path = os.path.join(SAMPLE_DIR, "temp_test_enc.dat")
        with open(temp_dat_path, "wb") as f:
            f.write(dat_bytes)

        # Decrypt the .dat file
        dec_fields = {
            "cipher": "super_encryption",
            "operation": "decrypt",
            "vigenere_key": "SENTINELKEY2026",
            "trans_key": "TACTICAL"
        }
        status, dec_res = test_post_multipart("/api/process/file", temp_dat_path, dec_fields)
        assert dec_res["success"] is True
        assert dec_res["download_filename"] == filename  # Original filename restored!

        # Download decrypted file and verify bit-for-bit exact SHA-256 match!
        status, restored_bytes = test_get(dec_res["download_url"])
        restored_sha256 = hashlib.sha256(restored_bytes).hexdigest()
        assert restored_sha256 == orig_sha256, f"Checksum mismatch for {filename}!"

        # Clean up temp file
        if os.path.exists(temp_dat_path):
            os.remove(temp_dat_path)

        print(f" -> [PASS] {filename} ({len(orig_bytes)}B): Packaged to .dat -> Restored bit-perfect (SHA-256: {orig_sha256[:16]}...)")

    # 5. Test SQLite Audit Log
    print("\n[5] Testing SQLite Audit Trail Retrieval...")
    status, audit_data = 200, json.loads(test_get("/api/audit-logs")[1].decode('utf-8'))
    assert audit_data["success"] is True
    total_ops = audit_data["stats"]["total_operations"]
    assert total_ops >= 18, f"Expected at least 18 logged ops, found {total_ops}"
    print(f" -> [PASS] SQLite Audit database verified with {total_ops} operations recorded.")

    print("\n=== ALL KRYPTO-SENTINEL TESTS COMPLETED WITH 100% SUCCESS! ===")

if __name__ == "__main__":
    run_all_e2e_tests()
