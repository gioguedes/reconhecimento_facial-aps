import pyotp
import qrcode
import json
from io import BytesIO
from base64 import b64encode
import config
from .encryption_service import EncryptionService

class MFAService:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.secrets_file = config.MFA_SECRETS_FILE
        self.encryption = EncryptionService()
        self.secrets = self._load_secrets()
        self._initialized = True

    def _load_secrets(self):
        if self.secrets_file.exists():
            try:
                with open(self.secrets_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.encryption.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode('utf-8'))
            except:
                return {}
        return {}

    def _save_secrets(self):
        try:
            self.secrets_file.parent.mkdir(parents=True, exist_ok=True)
            json_data = json.dumps(self.secrets, indent=2)
            encrypted_data = self.encryption.encrypt(json_data.encode('utf-8'))

            with open(self.secrets_file, 'wb') as f:
                f.write(encrypted_data)
        except:
            pass

    def generate_secret(self, username):
        secret = pyotp.random_base32()
        self.secrets[username] = secret
        self._save_secrets()
        return secret

    def get_secret(self, username):
        return self.secrets.get(username)

    def remove_secret(self, username):
        if username in self.secrets:
            del self.secrets[username]
            self._save_secrets()

    def generate_qr_code(self, username, secret, issuer="Sistema Reconhecimento Facial"):
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=username, issuer_name=issuer)

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = b64encode(buffer.getvalue()).decode('utf-8')

        return f"data:image/png;base64,{img_base64}"

    def verify_code(self, username, code):
        secret = self.get_secret(username)
        if not secret:
            return False

        code = code.strip().replace(' ', '')
        if not code.isdigit() or len(code) != 6:
            return False

        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    def user_has_mfa(self, username):
        return username in self.secrets
