import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.environ.get('SECRET_KEY', 'tnp-vault-sentinel-key-2026-secure')
MAX_CONTENT_LENGTH = 64 * 1024 * 1024  # 64 MB
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'temp_uploads')
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'temp_downloads')
DATABASE_PATH = os.path.join(BASE_DIR, 'krypto_audit.db')
SAMPLE_DATA_PATH = os.path.join(BASE_DIR, 'sample_data')
