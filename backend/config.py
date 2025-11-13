from pathlib import Path

BASE_DIR = Path(__file__).parent
DATABASE_DIR = BASE_DIR / 'database2'
LOGS_DIR = BASE_DIR / 'logs'
MODELS_DIR = BASE_DIR / 'models'

# Arquivos do sistema
ENCODINGS_FILE = DATABASE_DIR / 'encodings_encrypted.dat'
ENCRYPTION_KEY_FILE = DATABASE_DIR / 'encryption.key'
KNOWN_FACES_DIR = DATABASE_DIR / 'known_faces'
MFA_SECRETS_FILE = DATABASE_DIR / 'mfa_secrets_encrypted.json'
CONFIG_JSON_FILE = BASE_DIR / 'config.json'
AUDIT_LOGS_FILE = LOGS_DIR / 'access_logs.json'

# Modelos
FACE_DETECTION_PROTOTXT = MODELS_DIR / 'deploy.prototxt'
FACE_DETECTION_MODEL = MODELS_DIR / 'res10_300x300_ssd_iter_140000.caffemodel'
FACENET_MODEL = MODELS_DIR / 'nn4.small2.v1.t7'

# Segurança
MFA_REQUIRED_LEVELS = [2, 3]
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 300

# Processamento de imagem
MIN_FACE_CONFIDENCE = 0.5
MIN_IMAGE_SIZE = (640, 480)
TARGET_IMAGE_SIZE = (1280, 720)

# Flask
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000
FLASK_DEBUG = True

CORS_ORIGINS = [
    'http://localhost:5500',
    'http://127.0.0.1:5500',
    'http://localhost:5501',
    'http://127.0.0.1:5501'
]

# Garantir que diretórios existem
for directory in [DATABASE_DIR, LOGS_DIR, MODELS_DIR, KNOWN_FACES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
