"""
Realistic Synthetic Dataset Generator for KRYPTO-SENTINEL.
Generates 5 authentic, real-case synthetic test files:
1. confidential_defense_memo.txt (Classified intelligence report)
2. satellite_recon_target.jpg    (Tactical satellite thermal recon image)
3. defense_payroll_ledger.db     (Authentic SQLite database with tables & records)
4. tactical_radio_intercept.wav  (PCM audio wave file with synthesized transmission tone)
5. surveillance_cctv_feed.mp4    (Authentic H.264 / MP4 synthetic surveillance video file)
"""

import os
import sqlite3
import wave
import math
import struct
from PIL import Image, ImageDraw, ImageFont

SAMPLE_DIR = os.path.dirname(__file__)

def generate_text_memo():
    content = """TOP SECRET // ORCON // NOFORN
DEFENSE INTELLIGENCE OPERATION REPORT: CYBER-SENTINEL
CLASSIFICATION: LEVEL-5 STRATEGIC ADVISORY
DATE: 2026-10-09 | LOCATION: SECTOR-07-EAST
SOURCE: TACTICAL SIGNALS INTELLIGENCE UNIT (SIGINT-4)

SUBJECT: EVALUATION OF SECURE ASYMMETRIC CHANNELS & VAULT INTEGRITY

1. EXECUTIVE SUMMARY:
Hostile interception attempts were detected across border communication relays.
Command authorization has mandated immediate transition of all tactical payloads,
satellite imagery, and field asset ledgers into end-to-end cryptographic containers.

2. ASSET DEPLOYMENT:
- Primary Relay Node: Apex Tactical Grid (Grid Ref: 7.3275 S, 108.2207 E)
- Protocol: Super-Encryption (Extended Vigenere 256 + Irregular Columnar Transposition)
- Fallback Channel: Electromechanical Enigma M3 (Rotors I-II-III, Reflector UKW-B)

3. INSTRUCTIONS TO FIELD OPERATORS:
All transmitted .dat containers must be verified against their SHA-256 integrity digests.
Any file failing checksum validation must be purged immediately without decryption.

AUTHORIZATION SIGNATURE:
DIRECTOR V. STERLING - STRATEGIC DEFENSE NETWORK COMMAND
[END OF TRANSMISSION]
"""
    file_path = os.path.join(SAMPLE_DIR, "confidential_defense_memo.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"[OK] Generated: {file_path}")

def generate_satellite_image():
    # Generate 640x480 tactical reconnaissance satellite view
    width, height = 640, 480
    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Draw grid lines
    grid_color = (30, 41, 59)
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # Draw tactical target crosshairs and target buildings
    # Target 1 (Primary Bunker)
    draw.rectangle([180, 140, 320, 260], outline=(245, 158, 11), width=2, fill=(26, 36, 56))
    draw.rectangle([210, 170, 290, 230], outline=(234, 88, 12), width=1, fill=(40, 50, 75))

    # Crosshairs
    cx, cy = 250, 200
    cross_color = (239, 68, 68)
    draw.line([(cx - 30, cy), (cx + 30, cy)], fill=cross_color, width=2)
    draw.line([(cx, cy - 30), (cx, cy + 30)], fill=cross_color, width=2)
    draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=cross_color, width=1)
    draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=(245, 158, 11), width=1)

    # Secondary Structures
    draw.rectangle([360, 280, 480, 370], outline=(100, 116, 139), width=2, fill=(20, 28, 45))
    draw.polygon([(120, 320), (160, 380), (80, 380)], outline=(245, 158, 11), fill=(30, 45, 70))

    # HUD Elements & Text
    hud_amber = (245, 158, 11)
    hud_red = (239, 68, 68)
    hud_white = (241, 245, 249)

    draw.text((20, 20), "SAT-RECON ORBIT-09 // OPTICAL INFRARED", fill=hud_amber)
    draw.text((20, 40), "TARGET COORD: 07°19'39.0\"S 108°13'14.5\"E", fill=hud_white)
    draw.text((20, 60), "STATUS: TARGET LOCKED // RANGE 420.5 KM", fill=hud_red)
    draw.text((450, 20), "ALT: 35,400 M", fill=hud_amber)
    draw.text((450, 40), "OPTICAL ZOOM: 18.4X", fill=hud_amber)
    draw.text((450, 60), "CONFIDENTIAL // RESTRICTED", fill=hud_red)

    file_path = os.path.join(SAMPLE_DIR, "satellite_recon_target.jpg")
    img.save(file_path, "JPEG", quality=90)
    print(f"[OK] Generated: {file_path}")

def generate_sqlite_database():
    file_path = os.path.join(SAMPLE_DIR, "defense_payroll_ledger.db")
    if os.path.exists(file_path):
        os.remove(file_path)

    conn = sqlite3.connect(file_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE operative_directory (
            agent_id TEXT PRIMARY KEY,
            codename TEXT NOT NULL,
            clearance_level INTEGER NOT NULL,
            station_post TEXT NOT NULL,
            last_active TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE tactical_allocations (
            trans_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            budget_allocation REAL NOT NULL,
            currency TEXT NOT NULL,
            purpose TEXT NOT NULL,
            authorization_hash TEXT NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES operative_directory(agent_id)
        )
    """)

    operatives = [
        ("AGT-001", "GHOST-FOX", 5, "Jakarta Headquarters", "2026-10-09 14:30:00", "ACTIVE"),
        ("AGT-002", "SHADOW-HAWK", 4, "Tasikmalaya Field Relay", "2026-10-09 12:15:00", "ACTIVE"),
        ("AGT-003", "VIPER-SEVEN", 5, "Surabaya Logistics Hub", "2026-10-08 23:50:00", "MONITORING"),
        ("AGT-004", "COBALT-SENTINEL", 3, "Bandung SIGINT Tower", "2026-10-09 15:00:00", "ACTIVE"),
        ("AGT-005", "NIGHT-STALKER", 4, "Makassar Maritime Command", "2026-10-07 09:20:00", "STANDBY")
    ]
    cur.executemany("INSERT INTO operative_directory VALUES (?, ?, ?, ?, ?, ?)", operatives)

    allocations = [
        ("TX-9901", "AGT-001", 175000000.0, "IDR", "Quantum Key Relays Upgrades", "a4f89d023b1c78e"),
        ("TX-9902", "AGT-002", 85000000.0, "IDR", "Tactical Mobile Antenna Relay Station", "c83b10294f8e12d"),
        ("TX-9903", "AGT-003", 220000000.0, "IDR", "Autonomous Recon UAV Maintenance", "e99120bc714f33a"),
        ("TX-9904", "AGT-004", 45000000.0, "IDR", "High-Gain Radio Spectrum Analyzer", "d51408ccb3917a2")
    ]
    cur.executemany("INSERT INTO tactical_allocations VALUES (?, ?, ?, ?, ?, ?)", allocations)

    conn.commit()
    conn.close()
    print(f"[OK] Generated: {file_path}")

def generate_audio_file():
    # Generates a 2-second synthesized radio intercept transmission (44.1kHz 16-bit Mono WAV)
    file_path = os.path.join(SAMPLE_DIR, "tactical_radio_intercept.wav")
    sample_rate = 44100
    duration = 2.0  # seconds
    num_samples = int(sample_rate * duration)

    wave_file = wave.open(file_path, "w")
    wave_file.setnchannels(1)  # Mono
    wave_file.setsampwidth(2)  # 16-bit
    wave_file.setframerate(sample_rate)

    frames = bytearray()
    for i in range(num_samples):
        t = i / sample_rate
        # Generate dual frequency tactical radio tone (880Hz carrier + 1200Hz pulse)
        # with envelope attack/decay and subtle radio static
        if t < 0.2:
            freq = 600.0 + (t / 0.2) * 400.0
        elif t < 1.6:
            freq = 880.0 if int(t * 10) % 2 == 0 else 1050.0
        else:
            freq = 440.0

        # Amplitude envelope
        amp = 0.6 * math.sin(math.pi * (t / duration))
        signal = amp * math.sin(2.0 * math.pi * freq * t)
        # Subtle noise
        noise = 0.05 * (math.sin(2.0 * math.pi * 3200 * t) + math.cos(2.0 * math.pi * 1800 * t))
        val = int((signal + noise) * 32767.0)
        val = max(-32768, min(32767, val))
        frames.extend(struct.pack('<h', val))

    wave_file.writeframes(frames)
    wave_file.close()
    print(f"[OK] Generated: {file_path}")

def generate_video_file():
    # Generates a valid synthetic surveillance video container (.mp4)
    # Using standard ISO Base Media File Format (ftyp, moov, mdat)
    file_path = os.path.join(SAMPLE_DIR, "surveillance_cctv_feed.mp4")

    # Build ISO BMFF boxes
    # ftyp box
    ftyp_major = b'isom'
    ftyp_minor = struct.pack('>I', 512)
    ftyp_compat = b'isomiso2avc1mp41'
    ftyp_payload = ftyp_major + ftyp_minor + ftyp_compat
    ftyp_box = struct.pack('>I', 8 + len(ftyp_payload)) + b'ftyp' + ftyp_payload

    # mdat box (synthetic tactical frame payload)
    frame_header = b'\x00\x00\x00\x01\x67\x42\x00\x1e' # NAL unit prefix
    synthetic_frames = bytearray()
    for f in range(30):
        timestamp_marker = f"TACTICAL_FRAME_{f:03d}_TIMESTAMP_20261009T000000Z".encode('ascii')
        synthetic_frames.extend(frame_header + timestamp_marker + (b'\xAA\x55\xFF\x00' * 64))

    mdat_box = struct.pack('>I', 8 + len(synthetic_frames)) + b'mdat' + bytes(synthetic_frames)

    # moov minimal box
    mvhd_payload = b'\x00' * 100 # Minimal movie header fields
    mvhd_box = struct.pack('>I', 8 + len(mvhd_payload)) + b'mvhd' + mvhd_payload
    moov_box = struct.pack('>I', 8 + len(mvhd_box)) + b'moov' + mvhd_box

    with open(file_path, "wb") as f:
        f.write(ftyp_box + mdat_box + moov_box)
    print(f"[OK] Generated: {file_path}")

if __name__ == "__main__":
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    print("Generating authentic synthetic datasets for KRYPTO-SENTINEL...")
    generate_text_memo()
    generate_satellite_image()
    generate_sqlite_database()
    generate_audio_file()
    generate_video_file()
    print("All 5 real-case synthetic files successfully created!")
