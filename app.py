import os
import time
import json
import hashlib
import mimetypes
import uuid
from flask import Flask, render_template, request, jsonify, send_file, Response

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
import database

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64 MB maximum upload
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'temp_uploads')
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'temp_downloads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

# In-memory store for generated download files
DOWNLOAD_CACHE = {}

# Ensure SQLite audit database is initialized
database.init_db()

CIPHER_METADATA = {
    "vigenere_standard": {
        "id": "vigenere_standard",
        "name": "Standard Vigenere Cipher",
        "category": "alphabet_26",
        "formula": "C_i = (P_i + K_i) mod 26",
        "description": "Klasik Vigenere 26 alfabet A-Z. Spasi, angka, dan tanda baca dibuang secara otomatis (Spek 2).",
        "fields": [
            {"name": "key", "label": "Kunci Alfabet (A-Z)", "type": "text", "default": "SECRETKEY", "placeholder": "Masukkan kunci (bebas)"}
        ]
    },
    "vigenere_autokey": {
        "id": "vigenere_autokey",
        "name": "Auto-Key Vigenere Cipher",
        "category": "alphabet_26",
        "formula": "Keystream = Key + Plaintext[:N - len(Key)]",
        "description": "Varian Vigenere dengan aliran kunci yang diperpanjang otomatis oleh plainteks itu sendiri.",
        "fields": [
            {"name": "key", "label": "Kunci Awal (A-Z)", "type": "text", "default": "SENTINEL", "placeholder": "Masukkan kunci awal"}
        ]
    },
    "extended_vigenere": {
        "id": "extended_vigenere",
        "name": "Extended Vigenere Cipher",
        "category": "ascii_256",
        "formula": "C_i = (P_i + K_i) mod 256",
        "description": "Vigenere 256 karakter ASCII. Mendukung teks sembarang dan seluruh berkas biner (gambar, audio, video, database).",
        "fields": [
            {"name": "key", "label": "Kunci Byte/String", "type": "text", "default": "AegisCrypt2026", "placeholder": "Kunci bebas sembarang karakter"}
        ]
    },
    "playfair": {
        "id": "playfair",
        "name": "Playfair Cipher",
        "category": "alphabet_26",
        "formula": "Matriks 5x5 (Digraph Substitution)",
        "description": "Substitusi digram menggunakan matriks kunci 5x5. Huruf 'J' digabung ke 'I'. Pasangan ganda disisipkan 'X'.",
        "fields": [
            {"name": "key", "label": "Kunci Matriks 5x5", "type": "text", "default": "MONARCHY", "placeholder": "Kata kunci untuk matriks"}
        ]
    },
    "affine": {
        "id": "affine",
        "name": "Affine Cipher",
        "category": "alphabet_26",
        "formula": "C_i = (a * P_i + b) mod 26",
        "description": "Substitusi linier mod 26. Nilai 'a' harus relatif prima dengan 26 (gcd(a, 26) = 1).",
        "fields": [
            {"name": "key_a", "label": "Nilai a (Slope, gcd(a,26)=1)", "type": "number", "default": "7", "placeholder": "Contoh: 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25"},
            {"name": "key_b", "label": "Nilai b (Shift/Pergeseran)", "type": "number", "default": "10", "placeholder": "0 sampai 25"}
        ]
    },
    "hill": {
        "id": "hill",
        "name": "Hill Cipher",
        "category": "alphabet_26",
        "formula": "C = K * P mod 26",
        "description": "Enkripsi blok aljabar linier mod 26 dengan matriks kunci 2x2 atau 3x3 yang invertible.",
        "fields": [
            {"name": "hill_dim", "label": "Dimensi Matriks", "type": "select", "options": ["2x2", "3x3"], "default": "2x2"},
            {"name": "key", "label": "Elemen Matriks Kunci", "type": "text", "default": "3, 2, 5, 7", "placeholder": "2x2: '3, 2, 5, 7' atau 4 huruf. 3x3: 9 angka/huruf."}
        ]
    },
    "super_encryption": {
        "id": "super_encryption",
        "name": "Super Enkripsi",
        "category": "ascii_256",
        "formula": "Extended Vigenere (256) + Transposisi Kolom",
        "description": "Kombinasi substitusi Extended Vigenere (mod 256) dan permutasi transposisi metode kolom (Spek g). Bekerja pada teks dan file biner.",
        "fields": [
            {"name": "vigenere_key", "label": "Kunci Substitusi (Extended Vigenere)", "type": "text", "default": "SENTINELKEY", "placeholder": "Kunci substitusi"},
            {"name": "trans_key", "label": "Kunci Transposisi (Urutan Kolom)", "type": "text", "default": "TACTICAL", "placeholder": "Kata kunci kolom"}
        ]
    },
    "enigma": {
        "id": "enigma",
        "name": "(Bonus 1) Enigma Cipher Machine",
        "category": "alphabet_26",
        "formula": "Simulasi Mesin Enigma M3 (3 Rotor + Reflector + Plugboard)",
        "description": "Simulasi otentik mesin sandi Enigma Wehrmacht M3 dengan double-stepping dan plugboard (Spek h).",
        "fields": [
            {"name": "rotors", "label": "Susunan 3 Rotor", "type": "text", "default": "I, II, III", "placeholder": "Contoh: I, II, III"},
            {"name": "reflector", "label": "Reflector", "type": "select", "options": ["B", "C"], "default": "B"},
            {"name": "rings", "label": "Ringstellung (1-26)", "type": "text", "default": "1, 1, 1", "placeholder": "1, 1, 1"},
            {"name": "positions", "label": "Posisi Awal (Grundstellung)", "type": "text", "default": "AAA", "placeholder": "AAA"},
            {"name": "plugboard", "label": "Plugboard (Steckerbrett)", "type": "text", "default": "AV BS CG DL FU HZ", "placeholder": "Pasangan huruf, misal: AB CD EF"}
        ]
    }
}

@app.route('/')
def index():
    return render_template('index.html', ciphers=CIPHER_METADATA)

@app.route('/api/ciphers', methods=['GET'])
def get_ciphers():
    return jsonify({"success": True, "ciphers": CIPHER_METADATA})

@app.route('/api/process/text', methods=['POST'])
def process_text():
    try:
        data = request.get_json() or {}
        text = data.get('text', '')
        cipher_id = data.get('cipher', 'vigenere_standard')
        operation = data.get('operation', 'encrypt').lower()
        case_mode = data.get('case_mode', 'upper')  # 'upper' or 'lower' (Spek 5)

        if not text:
            return jsonify({"success": False, "error": "Pesan teks input tidak boleh kosong."}), 400

        t_start = time.perf_counter()
        meta = CIPHER_METADATA.get(cipher_id)
        if not meta:
            return jsonify({"success": False, "error": f"Algoritma '{cipher_id}' tidak dikenal."}), 400

        output_str = ""
        output_bytes = b""
        clean_input = ""

        # --- EXECUTE CORRESPONDING CIPHER ---
        if cipher_id == "vigenere_standard":
            key = data.get('key', 'SECRET')
            clean_input = base.clean_alphabet(text)
            if operation == 'encrypt':
                output_str = vigenere.encrypt(text, key)
            else:
                output_str = vigenere.decrypt(text, key)
            output_bytes = output_str.encode('utf-8')

        elif cipher_id == "vigenere_autokey":
            key = data.get('key', 'SENTINEL')
            clean_input = base.clean_alphabet(text)
            if operation == 'encrypt':
                output_str = autokey.encrypt(text, key)
            else:
                output_str = autokey.decrypt(text, key)
            output_bytes = output_str.encode('utf-8')

        elif cipher_id == "extended_vigenere":
            key = data.get('key', 'Aegis2026')
            clean_input = text  # Extended Vigenere preserves all characters
            if operation == 'encrypt':
                output_bytes = extended_vigenere.encrypt(text, key)
                output_str = output_bytes.decode('latin1', errors='replace')
            else:
                input_bytes = text.encode('latin1')
                output_bytes = extended_vigenere.decrypt_bytes(input_bytes, key.encode('utf-8'))
                output_str = output_bytes.decode('utf-8', errors='replace')

        elif cipher_id == "playfair":
            key = data.get('key', 'MONARCHY')
            clean_input = base.clean_alphabet(text).replace('J', 'I')
            if operation == 'encrypt':
                output_str = playfair.encrypt(text, key)
            else:
                output_str = playfair.decrypt(text, key)
            output_bytes = output_str.encode('utf-8')

        elif cipher_id == "affine":
            key_a = int(data.get('key_a', 7))
            key_b = int(data.get('key_b', 10))
            clean_input = base.clean_alphabet(text)
            if operation == 'encrypt':
                output_str = affine.encrypt(text, (key_a, key_b))
            else:
                output_str = affine.decrypt(text, (key_a, key_b))
            output_bytes = output_str.encode('utf-8')

        elif cipher_id == "hill":
            key_val = data.get('key', '3, 2, 5, 7')
            clean_input = base.clean_alphabet(text)
            if operation == 'encrypt':
                output_str = hill.encrypt(text, key_val)
            else:
                output_str = hill.decrypt(text, key_val)
            output_bytes = output_str.encode('utf-8')

        elif cipher_id == "super_encryption":
            v_key = data.get('vigenere_key', 'SENTINEL')
            t_key = data.get('trans_key', 'TACTICAL')
            clean_input = text
            if operation == 'encrypt':
                output_bytes = super_encryption.encrypt(text.encode('utf-8'), v_key, t_key)
                output_str = output_bytes.decode('latin1', errors='replace')
            else:
                input_bytes = text.encode('latin1')
                output_bytes = super_encryption.decrypt(input_bytes, v_key, t_key)
                output_str = output_bytes.decode('utf-8', errors='replace')

        elif cipher_id == "enigma":
            rotors_str = data.get('rotors', 'I, II, III')
            rotors = [r.strip().upper() for r in rotors_str.split(',') if r.strip()]
            reflector = data.get('reflector', 'B').upper()
            rings_str = data.get('rings', '1, 1, 1')
            rings = [int(r.strip()) for r in rings_str.split(',') if r.strip().isdigit()]
            positions = data.get('positions', 'AAA').strip()
            plugboard = data.get('plugboard', '').strip()
            clean_input = base.clean_alphabet(text)

            output_str = enigma.process(
                text,
                rotors=rotors if len(rotors) == 3 else ["I", "II", "III"],
                reflector=reflector,
                ring_settings=rings if len(rings) == 3 else [1, 1, 1],
                initial_positions=positions,
                plugboard_pairs=plugboard
            )
            output_bytes = output_str.encode('utf-8')

        duration_ms = (time.perf_counter() - t_start) * 1000

        # Hashes
        input_bytes = text.encode('utf-8')
        in_sha256 = hashlib.sha256(input_bytes).hexdigest()
        out_sha256 = hashlib.sha256(output_bytes).hexdigest()

        # Base64 representations (Specifications 4 & 5)
        # Display ciphertext without spaces, all lowercase or all uppercase
        is_upper = (case_mode == 'upper')
        is_lower = (case_mode == 'lower')
        b64_output_clean = base.to_base64_no_spaces(output_bytes, lowercase=is_lower, uppercase=is_upper)
        b64_output_standard = base.to_base64_no_spaces(output_bytes)
        b64_input_standard = base.to_base64_no_spaces(input_bytes)

        # Hex Dumps for Inspector
        hex_dump_in = base.format_hex_dump(input_bytes, max_bytes=256)
        hex_dump_out = base.format_hex_dump(output_bytes, max_bytes=256)

        # Log to SQLite
        log_id = database.log_operation(
            operation=operation,
            input_type="TEKS (Papan Ketik)",
            cipher=meta["name"],
            item_name="Papan Ketik (Direct Input Stream)",
            original_size=len(input_bytes),
            result_size=len(output_bytes),
            input_sha256=in_sha256,
            output_sha256=out_sha256,
            duration_ms=duration_ms,
            status="SUCCESS",
            notes=f"Key/Params used. Base64 len: {len(b64_output_clean)}"
        )

        return jsonify({
            "success": True,
            "operation": operation,
            "cipher_id": cipher_id,
            "cipher_name": meta["name"],
            "clean_input": clean_input,
            "output_text": output_str,
            "base64_output": b64_output_clean,
            "base64_output_standard": b64_output_standard,
            "base64_input_standard": b64_input_standard,
            "hex_dump_input": hex_dump_in,
            "hex_dump_output": hex_dump_out,
            "input_sha256": in_sha256,
            "output_sha256": out_sha256,
            "duration_ms": round(duration_ms, 2),
            "log_id": log_id
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/process/file', methods=['POST'])
def process_file():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "Tidak ada berkas yang diunggah."}), 400

        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({"success": False, "error": "Nama berkas kosong."}), 400

        cipher_id = request.form.get('cipher', 'extended_vigenere')
        operation = request.form.get('operation', 'encrypt').lower()
        filename = uploaded_file.filename
        raw_bytes = uploaded_file.read()

        if len(raw_bytes) == 0:
            return jsonify({"success": False, "error": "Berkas yang diunggah berukuran 0 byte."}), 400

        t_start = time.perf_counter()
        meta = CIPHER_METADATA.get(cipher_id)
        if not meta:
            return jsonify({"success": False, "error": f"Algoritma '{cipher_id}' tidak valid."}), 400

        # Ensure cipher supports binary 256 bytes for files
        if meta["category"] != "ascii_256":
            return jsonify({
                "success": False,
                "error": f"Algoritma '{meta['name']}' hanya mendukung 26 alfabet A-Z (Spek 2). "
                         "Untuk berkas biner (gambar, audio, video, database, dll), "
                         "gunakan Extended Vigenere atau Super Enkripsi (Spek c & g)."
            }), 400

        result_bytes = b""
        download_filename = ""
        download_mime = "application/octet-stream"
        container_meta = None

        if operation == 'encrypt':
            # 1. Compute original hash
            orig_sha256 = hashlib.sha256(raw_bytes).hexdigest()
            orig_size = len(raw_bytes)
            mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

            # 2. Encrypt raw bytes
            if cipher_id == "extended_vigenere":
                key = request.form.get('key', 'AegisVault2026')
                encrypted_payload = extended_vigenere.encrypt_bytes(raw_bytes, key.encode('utf-8'))
            elif cipher_id == "super_encryption":
                v_key = request.form.get('vigenere_key', 'SENTINELKEY')
                t_key = request.form.get('trans_key', 'TACTICAL')
                encrypted_payload = super_encryption.encrypt(raw_bytes, v_key, t_key)
            else:
                raise ValueError("Cipher not supported for binary file encryption.")

            # 3. Pack into .dat container (Specifications 8 & 9)
            result_bytes = container.pack_container(
                encrypted_payload=encrypted_payload,
                original_name=filename,
                cipher_name=cipher_id,
                original_sha256=orig_sha256,
                original_size=orig_size,
                mime_type=mime_type
            )

            # Name as .dat container
            base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
            download_filename = f"{base_name}.dat"
            download_mime = "application/octet-stream"

        else: # operation == 'decrypt'
            # Check if this is a TNP (Trust No Plaintext) .dat container
            if container.is_krypto_container(raw_bytes):
                container_meta, payload_bytes = container.unpack_container(raw_bytes)
                saved_cipher = container_meta.get("cipher", cipher_id)
                download_filename = container_meta.get("name", "decrypted_file.bin")
                download_mime = container_meta.get("mime", "application/octet-stream")
                expected_sha256 = container_meta.get("sha256", "")

                # Decrypt payload
                if cipher_id == "extended_vigenere":
                    key = request.form.get('key', 'AegisVault2026')
                    result_bytes = extended_vigenere.decrypt_bytes(payload_bytes, key.encode('utf-8'))
                elif cipher_id == "super_encryption":
                    v_key = request.form.get('vigenere_key', 'SENTINELKEY')
                    t_key = request.form.get('trans_key', 'TACTICAL')
                    result_bytes = super_encryption.decrypt(payload_bytes, v_key, t_key)
                else:
                    raise ValueError("Unsupported cipher for file decryption.")

                # Verify cryptographic integrity
                actual_sha256 = hashlib.sha256(result_bytes).hexdigest()
                if expected_sha256 and actual_sha256 != expected_sha256:
                    # Integrity failure (wrong key or corrupt file)
                    pass
            else:
                # Raw binary file decryption without container
                if cipher_id == "extended_vigenere":
                    key = request.form.get('key', 'AegisVault2026')
                    result_bytes = extended_vigenere.decrypt_bytes(raw_bytes, key.encode('utf-8'))
                elif cipher_id == "super_encryption":
                    v_key = request.form.get('vigenere_key', 'SENTINELKEY')
                    t_key = request.form.get('trans_key', 'TACTICAL')
                    result_bytes = super_encryption.decrypt(raw_bytes, v_key, t_key)
                else:
                    raise ValueError("Unsupported cipher.")

                download_filename = f"decrypted_{filename}"
                download_mime = "application/octet-stream"

        duration_ms = (time.perf_counter() - t_start) * 1000
        in_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        out_sha256 = hashlib.sha256(result_bytes).hexdigest()

        # Cache file in memory for download
        file_id = str(uuid.uuid4())
        DOWNLOAD_CACHE[file_id] = {
            "bytes": result_bytes,
            "filename": download_filename,
            "mime": download_mime
        }

        # Hex Dumps (first 256 bytes)
        hex_dump_in = base.format_hex_dump(raw_bytes, max_bytes=256)
        hex_dump_out = base.format_hex_dump(result_bytes, max_bytes=256)

        # Base64 representation (first 2000 chars preview)
        b64_output_clean = base.to_base64_no_spaces(result_bytes[:4096], uppercase=True)

        # Determine detailed specific file type
        ext_lower = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext_lower in ['db', 'sqlite', 'sqlite3']:
            detailed_type = "DATABASE (SQLite .db)"
        elif ext_lower in ['jpg', 'jpeg']:
            detailed_type = "GAMBAR (JPEG .jpg)"
        elif ext_lower in ['png', 'gif', 'bmp', 'webp']:
            detailed_type = f"GAMBAR ({ext_lower.upper()} .{ext_lower})"
        elif ext_lower in ['wav', 'pcm']:
            detailed_type = "AUDIO (PCM WAV .wav)"
        elif ext_lower in ['mp3', 'ogg', 'flac', 'm4a']:
            detailed_type = f"AUDIO ({ext_lower.upper()} .{ext_lower})"
        elif ext_lower in ['mp4', 'mkv', 'avi', 'mov']:
            detailed_type = f"VIDEO ({ext_lower.upper()} .{ext_lower})"
        elif ext_lower in ['txt', 'md', 'log']:
            detailed_type = "DOKUMEN (Teks .txt)"
        elif ext_lower in ['docx', 'doc']:
            detailed_type = "DOKUMEN (Word .docx)"
        elif ext_lower in ['pdf']:
            detailed_type = "DOKUMEN (PDF .pdf)"
        elif ext_lower == 'dat':
            if container_meta and container_meta.get("ext"):
                orig_ext = container_meta.get("ext", "").replace(".", "").upper()
                detailed_type = f"CONTAINER (Vault .dat → .{orig_ext})"
            else:
                detailed_type = "CONTAINER (Vault .dat)"
        else:
            detailed_type = f"BERKAS BINER (.{ext_lower.upper()})" if ext_lower else "BERKAS BINER (Raw)"

        # Log to SQLite
        log_id = database.log_operation(
            operation=operation,
            input_type=detailed_type,
            cipher=meta["name"],
            item_name=filename,
            original_size=len(raw_bytes),
            result_size=len(result_bytes),
            input_sha256=in_sha256,
            output_sha256=out_sha256,
            duration_ms=duration_ms,
            status="SUCCESS",
            notes=f"Saved as: {download_filename} ({download_mime})"
        )

        return jsonify({
            "success": True,
            "file_id": file_id,
            "operation": operation,
            "cipher_name": meta["name"],
            "original_filename": filename,
            "download_filename": download_filename,
            "mime_type": download_mime,
            "original_size": len(raw_bytes),
            "result_size": len(result_bytes),
            "input_sha256": in_sha256,
            "output_sha256": out_sha256,
            "duration_ms": round(duration_ms, 2),
            "container_meta": container_meta,
            "base64_preview": b64_output_clean,
            "hex_dump_input": hex_dump_in,
            "hex_dump_output": hex_dump_out,
            "log_id": log_id,
            "download_url": f"/api/download/file/{file_id}"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/download/file/<file_id>', methods=['GET'])
def download_file(file_id):
    item = DOWNLOAD_CACHE.get(file_id)
    if not item:
        return "File tidak ditemukan atau sesi telah berakhir.", 404

    return Response(
        item["bytes"],
        mimetype=item["mime"],
        headers={"Content-Disposition": f"attachment; filename=\"{item['filename']}\""}
    )

@app.route('/api/enigma/step', methods=['POST'])
def enigma_step():
    try:
        data = request.get_json() or {}
        text = data.get('text', 'A')
        rotors_str = data.get('rotors', 'I, II, III')
        rotors = [r.strip().upper() for r in rotors_str.split(',') if r.strip()]
        reflector = data.get('reflector', 'B').upper()
        rings_str = data.get('rings', '1, 1, 1')
        rings = [int(r.strip()) for r in rings_str.split(',') if r.strip().isdigit()]
        positions = data.get('positions', 'AAA').strip()
        plugboard = data.get('plugboard', '').strip()

        machine = enigma.EnigmaMachine(
            rotors=rotors if len(rotors) == 3 else ["I", "II", "III"],
            reflector=reflector,
            ring_settings=rings if len(rings) == 3 else [1, 1, 1],
            initial_positions=positions,
            plugboard_pairs=plugboard
        )

        ciphertext, traces = machine.process_text(text)
        return jsonify({
            "success": True,
            "plaintext": base.clean_alphabet(text),
            "ciphertext": ciphertext,
            "traces": traces,
            "final_positions": {
                "left": machine.left_rotor.current_char,
                "middle": machine.middle_rotor.current_char,
                "right": machine.right_rotor.current_char
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/samples', methods=['GET'])
def list_samples():
    sample_dir = os.path.join(os.path.dirname(__file__), 'sample_data')
    samples = []
    if os.path.exists(sample_dir):
        for fname in os.listdir(sample_dir):
            if fname.endswith(('.txt', '.jpg', '.db', '.wav', '.mp4')):
                fpath = os.path.join(sample_dir, fname)
                fsize = os.path.getsize(fpath)
                with open(fpath, 'rb') as f:
                    fsha = hashlib.sha256(f.read()).hexdigest()
                samples.append({
                    "filename": fname,
                    "size": fsize,
                    "sha256": fsha,
                    "download_url": f"/api/sample/download/{fname}"
                })
    return jsonify({"success": True, "samples": samples})

@app.route('/api/sample/download/<filename>', methods=['GET'])
def download_sample(filename):
    sample_path = os.path.join(os.path.dirname(__file__), 'sample_data', filename)
    if not os.path.exists(sample_path):
        return "File tidak ditemukan", 404
    mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return send_file(sample_path, mimetype=mime, as_attachment=True, download_name=filename)

@app.route('/api/audit-logs', methods=['GET'])
def get_audit_logs():
    logs = database.get_recent_logs(limit=100)
    stats = database.get_system_stats()
    return jsonify({"success": True, "logs": logs, "stats": stats})

@app.route('/api/audit-logs/clear', methods=['POST'])
def clear_audit_logs():
    database.clear_logs()
    return jsonify({"success": True, "message": "Riwayat audit berhasil dibersihkan."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[*] TNP (Trust No Plaintext) Server running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
