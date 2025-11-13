import cv2
import json
import numpy as np
import pickle
from datetime import datetime
from pathlib import Path

import config
from models.user import User
from utils.image_utils import preprocess_image
from .audit_service import AuditService
from .encryption_service import EncryptionService
from .mfa_service import MFAService

class FaceDetectorDNN:
    def __init__(self):
        prototxt = str(config.FACE_DETECTION_PROTOTXT)
        caffemodel = str(config.FACE_DETECTION_MODEL)

        if not Path(prototxt).exists() or not Path(caffemodel).exists():
            raise FileNotFoundError(f"Modelos de detecção não encontrados")

        self.net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)

    def detect(self, image, confidence_threshold=0.5):
        h, w = image.shape[:2]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )

        self.net.setInput(blob)
        detections = self.net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > confidence_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")

                x = max(0, x1)
                y = max(0, y1)
                width = min(w - x, x2 - x1)
                height = min(h - y, y2 - y1)

                if width > 0 and height > 0:
                    faces.append((x, y, width, height))

        return faces

class FaceEmbedder:
    def __init__(self):
        model_path = str(config.FACENET_MODEL)

        if not Path(model_path).exists():
            raise FileNotFoundError(f"Modelo FaceNet não encontrado")

        self.net = cv2.dnn.readNetFromTorch(model_path)

    def extract(self, face_image):
        face_blob = cv2.dnn.blobFromImage(
            face_image,
            1.0 / 255,
            (96, 96),
            (0, 0, 0),
            swapRB=True,
            crop=False
        )

        self.net.setInput(face_blob)
        embedding = self.net.forward()

        embedding = embedding.flatten()
        embedding = embedding / np.linalg.norm(embedding)

        return embedding

class FacialRecognitionService:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.detector = FaceDetectorDNN()
        self.embedder = FaceEmbedder()
        self.encryption = EncryptionService()
        self.mfa_service = MFAService()
        self.audit_service = AuditService()

        self.encodings_file = config.ENCODINGS_FILE
        self.known_faces_dir = config.KNOWN_FACES_DIR
        self.config_file = config.CONFIG_JSON_FILE

        self.users = self._load_users()
        self.thresholds = self._load_thresholds()

        self._initialized = True

    def _load_users(self):
        if not self.encodings_file.exists():
            return {}

        try:
            with open(self.encodings_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.encryption.decrypt(encrypted_data)
            data = pickle.loads(decrypted_data)

            users = {}
            for name, user_data in data.items():
                user = User(
                    name=user_data['name'],
                    permission_level=user_data['permission_level'],
                    face_encodings=user_data['face_encodings'],
                    mfa_secret=user_data.get('mfa_secret'),
                    enrolled_date=user_data.get('enrolled_date'),
                    last_access=user_data.get('last_access'),
                    failed_attempts=user_data.get('failed_attempts', 0),
                    lockout_until=user_data.get('lockout_until')
                )
                users[name] = user

            return users
        except:
            return {}

    def _save_users(self):
        try:
            self.encodings_file.parent.mkdir(parents=True, exist_ok=True)

            data = {}
            for name, user in self.users.items():
                data[name] = {
                    'name': user.name,
                    'permission_level': user.permission_level,
                    'face_encodings': user.face_encodings,
                    'mfa_secret': user.mfa_secret,
                    'enrolled_date': user.enrolled_date,
                    'last_access': user.last_access,
                    'failed_attempts': user.failed_attempts,
                    'lockout_until': user.lockout_until
                }

            pickled_data = pickle.dumps(data)
            encrypted_data = self.encryption.encrypt(pickled_data)

            with open(self.encodings_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            raise RuntimeError(f"Erro ao salvar usuários: {str(e)}")

    def _load_thresholds(self):
        default_thresholds = {1: 0.70, 2: 0.80, 3: 0.85}

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)

                return {
                    1: config_data.get('nivel_1_threshold', 0.70),
                    2: config_data.get('nivel_2_threshold', 0.80),
                    3: config_data.get('nivel_3_threshold', 0.85)
                }
            except:
                pass

        return default_thresholds

    def _save_thresholds(self):
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            config_data = {
                'nivel_1_threshold': self.thresholds[1],
                'nivel_2_threshold': self.thresholds[2],
                'nivel_3_threshold': self.thresholds[3],
                'last_updated': datetime.now().isoformat()
            }

            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Erro ao salvar configurações: {str(e)}")

    def detect_face(self, image):
        faces = self.detector.detect(image, confidence_threshold=config.MIN_FACE_CONFIDENCE)

        if len(faces) == 0:
            return None

        return max(faces, key=lambda f: f[2] * f[3])

    def extract_embedding(self, image, face_bbox):
        x, y, w, h = face_bbox

        margin = int(max(w, h) * 0.2)
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(image.shape[1], x + w + margin)
        y2 = min(image.shape[0], y + h + margin)

        face_image = image[y1:y2, x1:x2]

        return self.embedder.extract(face_image)

    def enroll_user(self, name, security_level, image):
        if name in self.users:
            self.audit_service.add_log(
                event_type="enrollment",
                user_id=name,
                decision="denied",
                reason="Usuário já cadastrado"
            )
            return False, "Usuário já cadastrado", None

        processed_image = preprocess_image(image)

        face_bbox = self.detect_face(processed_image)
        if not face_bbox:
            self.audit_service.add_log(
                event_type="enrollment",
                user_id=name,
                decision="denied",
                reason="Nenhuma face detectada"
            )
            return False, "Nenhuma face detectada na imagem", None

        embedding = self.extract_embedding(processed_image, face_bbox)

        user = User(
            name=name,
            permission_level=security_level,
            face_encodings=[embedding.tolist()]
        )

        qr_code = None
        if user.requires_mfa():
            secret = self.mfa_service.generate_secret(name)
            user.mfa_secret = secret
            qr_code = self.mfa_service.generate_qr_code(name, secret)

        self.users[name] = user
        self._save_users()

        try:
            image_path = self.known_faces_dir / f"{name}.jpg"
            cv2.imwrite(str(image_path), image)
        except:
            pass

        self.audit_service.add_log(
            event_type="enrollment",
            user_id=name,
            decision="granted",
            reason=f"Cadastro realizado (nível {security_level})"
        )

        return True, "Usuário cadastrado com sucesso", qr_code

    def authenticate_user(self, image):
        processed_image = preprocess_image(image)

        face_bbox = self.detect_face(processed_image)
        if not face_bbox:
            self.audit_service.add_log(
                event_type="authentication",
                user_id=None,
                decision="denied",
                reason="Nenhuma face detectada"
            )
            return False, None, 0, 0.0, False, "Nenhuma face detectada"

        embedding = self.extract_embedding(processed_image, face_bbox)

        best_match = None
        best_similarity = -1.0

        for name, user in self.users.items():
            if user.is_locked_out():
                continue

            for stored_embedding in user.face_encodings:
                stored_array = np.array(stored_embedding)
                similarity = np.dot(embedding, stored_array)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = user

        if not best_match:
            self.audit_service.add_log(
                event_type="authentication",
                user_id="unknown",
                decision="denied",
                confidence=best_similarity,
                reason="Face não reconhecida"
            )
            return False, None, 0, 0.0, False, "Face não reconhecida"

        threshold = self.thresholds[best_match.permission_level]

        if best_similarity < threshold:
            best_match.increment_failed_attempts(config.LOCKOUT_DURATION)
            self._save_users()

            self.audit_service.add_log(
                event_type="authentication",
                user_id=best_match.name,
                decision="denied",
                confidence=best_similarity,
                reason=f"Confiança baixa ({best_similarity:.2f} < {threshold:.2f})"
            )

            return False, None, 0, best_similarity, False, "Confiança insuficiente"

        requires_mfa = best_match.requires_mfa()

        if not requires_mfa:
            best_match.reset_failed_attempts()
            best_match.update_last_access()
            self._save_users()

            self.audit_service.add_log(
                event_type="authentication",
                user_id=best_match.name,
                decision="granted",
                confidence=best_similarity,
                mfa_used=False,
                reason="Autenticação bem-sucedida"
            )

        return True, best_match.name, best_match.permission_level, best_similarity, requires_mfa, "Face reconhecida"

    def verify_mfa_and_grant_access(self, username, otp_code):
        user = self.users.get(username)
        if not user:
            return False, "Usuário não encontrado"

        if self.mfa_service.verify_code(username, otp_code):
            user.reset_failed_attempts()
            user.update_last_access()
            self._save_users()

            self.audit_service.add_log(
                event_type="mfa_verification",
                user_id=username,
                decision="granted",
                mfa_used=True,
                reason="MFA verificado"
            )

            return True, "Acesso concedido"
        else:
            user.increment_failed_attempts(config.LOCKOUT_DURATION)
            self._save_users()

            self.audit_service.add_log(
                event_type="mfa_verification",
                user_id=username,
                decision="denied",
                mfa_used=True,
                reason="Código MFA inválido"
            )

            return False, "Código MFA inválido"

    def update_thresholds(self, level_1, level_2, level_3):
        try:
            self.thresholds = {1: level_1, 2: level_2, 3: level_3}
            self._save_thresholds()

            self.audit_service.add_log(
                event_type="config_update",
                user_id="admin",
                decision="granted",
                reason=f"Thresholds atualizados"
            )

            return True, "Configurações atualizadas"
        except Exception as e:
            return False, f"Erro: {str(e)}"

    def get_all_users(self):
        return [user.to_dict() for user in self.users.values()]

    def delete_user(self, username):
        if username not in self.users:
            return False, "Usuário não encontrado"

        del self.users[username]
        self._save_users()

        self.mfa_service.remove_secret(username)

        try:
            image_path = self.known_faces_dir / f"{username}.jpg"
            if image_path.exists():
                image_path.unlink()
        except:
            pass

        self.audit_service.add_log(
            event_type="user_deletion",
            user_id=username,
            decision="granted",
            reason="Usuário removido"
        )

        return True, "Usuário removido com sucesso"

    def get_user(self, username):
        user = self.users.get(username)
        if not user:
            return None
        return user.to_dict()

    def get_thresholds(self):
        return {
            'nivel_1_threshold': self.thresholds[1],
            'nivel_2_threshold': self.thresholds[2],
            'nivel_3_threshold': self.thresholds[3]
        }
