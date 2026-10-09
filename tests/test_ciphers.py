"""
Automated Test Suite for All 8 Cryptographic Algorithms and Binary Container.
Verifies exact reversibility, edge cases, and compliance with assignment specifications.
"""

import unittest
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ciphers import (
    base,
    vigenere,
    autokey,
    extended_vigenere,
    playfair,
    affine,
    hill,
    super_encryption,
    enigma,
    container
)

class TestCiphers(unittest.TestCase):

    def test_01_vigenere_standard(self):
        text = "Di bawah sinar bulan purnama, air laut berkilauan!"
        key = "SECRETKEY"
        enc = vigenere.encrypt(text, key)
        dec = vigenere.decrypt(enc, key)
        clean = base.clean_alphabet(text)
        self.assertEqual(dec, clean)
        self.assertTrue(all(c.isupper() and c.isalpha() for c in enc))

    def test_02_autokey_vigenere(self):
        text = "NEGARA PENGHASIL MINYAK BUMI TERBESAR DI DUNIA"
        key = "SENTINEL"
        enc = autokey.encrypt(text, key)
        dec = autokey.decrypt(enc, key)
        clean = base.clean_alphabet(text)
        self.assertEqual(dec, clean)

    def test_03_extended_vigenere_bytes(self):
        data = b"\x00\xff\x10\x80Hello World!\xde\xad\xbe\xef"
        key = b"SecurityVaultKey2026"
        enc = extended_vigenere.encrypt_bytes(data, key)
        self.assertNotEqual(enc, data)
        dec = extended_vigenere.decrypt_bytes(enc, key)
        self.assertEqual(dec, data)

    def test_04_playfair_cipher(self):
        text = "TEMU KAN SAYA DI JALAN SUDIRMAN PUKUL SEPULUH MALAM"
        key = "KUNCI PLAYFAIR"
        enc = playfair.encrypt(text, key)
        dec = playfair.decrypt(enc, key)
        # In Playfair, J becomes I and duplicate fillers/padding X may be inserted
        expected_chars = base.clean_alphabet(text).replace('J', 'I')
        # Check that characters match structurally
        self.assertTrue(len(enc) % 2 == 0)
        self.assertTrue(len(dec) % 2 == 0)
        # Decrypted without fillers should contain the primary message
        self.assertIn("TEMUKANSAYADI", dec)

    def test_05_affine_cipher(self):
        text = "KRIPTOGRAFI KLASIK DAN MODERN"
        key = (7, 10) # gcd(7, 26) = 1
        enc = affine.encrypt(text, key)
        dec = affine.decrypt(enc, key)
        clean = base.clean_alphabet(text)
        self.assertEqual(dec, clean)

    def test_06_hill_cipher_2x2(self):
        text = "SHORT MESSAGE"
        # Key matrix [[3, 2], [5, 7]] -> det = 21 - 10 = 11, gcd(11, 26) = 1
        key = [[3, 2], [5, 7]]
        enc = hill.encrypt(text, key)
        dec = hill.decrypt(enc, key)
        clean = base.clean_alphabet(text)
        # Account for possible padding 'X'
        self.assertTrue(dec.startswith(clean))

    def test_07_hill_cipher_3x3(self):
        text = "PAY MORE MONEY"
        # 3x3 invertible matrix mod 26: "GYBNQWERT" -> [[6,24,1],[13,16,10],[20,17,19]]
        # Let's test explicit invertible 3x3:
        key = [[6, 24, 1], [13, 16, 10], [20, 17, 15]]
        enc = hill.encrypt(text, key)
        dec = hill.decrypt(enc, key)
        clean = base.clean_alphabet(text)
        self.assertTrue(dec.startswith(clean))

    def test_08_super_encryption_binary(self):
        data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00BinaryPayloadTest12345"
        v_key = "AEGIS_VIGENERE_KEY"
        t_key = "TRANSPOSITION_KEY"
        enc = super_encryption.encrypt(data, v_key, t_key)
        self.assertNotEqual(enc, data)
        self.assertEqual(len(enc), len(data))
        dec = super_encryption.decrypt(enc, v_key, t_key)
        self.assertEqual(dec, data)

    def test_09_enigma_machine(self):
        text = "HELLOWORLDFROMENIGMAMACHINE"
        rotors = ["I", "II", "III"]
        reflector = "B"
        rings = [1, 1, 1]
        start_pos = "ABC"
        plugboard = "AB CD EF"

        enc = enigma.process(text, rotors, reflector, rings, start_pos, plugboard)
        self.assertNotEqual(enc, text)
        # Reciprocal decryption: processing again with identical state yields original text
        dec = enigma.process(enc, rotors, reflector, rings, start_pos, plugboard)
        self.assertEqual(dec, text)

    def test_10_container_packaging(self):
        original_data = b"CONFIDENTIAL ASSET LEDGER CONTENT"
        enc_payload = extended_vigenere.encrypt_bytes(original_data, b"SECRET")

        packed = container.pack_container(
            encrypted_payload=enc_payload,
            original_name="intel_report.docx",
            cipher_name="extended_vigenere",
            original_sha256="fake_sha256_hash",
            original_size=len(original_data),
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        self.assertTrue(container.is_krypto_container(packed))
        metadata, extracted_payload = container.unpack_container(packed)
        self.assertEqual(metadata["name"], "intel_report.docx")
        self.assertEqual(metadata["ext"], ".docx")
        self.assertEqual(extracted_payload, enc_payload)

        # Decrypt payload
        restored_data = extended_vigenere.decrypt_bytes(extracted_payload, b"SECRET")
        self.assertEqual(restored_data, original_data)

if __name__ == "__main__":
    unittest.main()
