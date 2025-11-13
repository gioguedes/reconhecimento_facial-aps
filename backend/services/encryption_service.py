from cryptography.fernet import Fernet
import config

class EncryptionService:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.key_file = config.ENCRYPTION_KEY_FILE
        self.cipher = self._load_or_create_key()
        self._initialized = True

    def _load_or_create_key(self):
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key)

        return Fernet(key)

    def encrypt(self, data):
        return self.cipher.encrypt(data)

    def decrypt(self, encrypted_data):
        try:
            return self.cipher.decrypt(encrypted_data)
        except Exception as e:
            raise ValueError(f"Erro ao descriptografar: {e}")

    def encrypt_string(self, text):
        encrypted = self.encrypt(text.encode('utf-8'))
        return encrypted.decode('utf-8')

    def decrypt_string(self, encrypted_text):
        decrypted = self.decrypt(encrypted_text.encode('utf-8'))
        return decrypted.decode('utf-8')
