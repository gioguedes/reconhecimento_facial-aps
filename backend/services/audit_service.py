import json
import hashlib
from datetime import datetime
import config

class AuditService:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.log_file = config.AUDIT_LOGS_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logs = self._load_logs()
        self._initialized = True

    def _load_logs(self):
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _save_logs(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)

    def _calculate_hash(self, log_entry, prev_hash):
        data = json.dumps(log_entry, sort_keys=True) + prev_hash
        return hashlib.sha256(data.encode()).hexdigest()

    def add_log(self, event_type, user_id, decision, confidence=0.0,
                reason="", mfa_used=False, ip_address="127.0.0.1"):
        prev_hash = self.logs[-1]["hash"] if self.logs else "0" * 64

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "user_id": user_id,
            "decision": decision,
            "confidence_score": confidence,
            "reason": reason,
            "mfa_used": mfa_used,
            "ip_address": ip_address
        }

        log_hash = self._calculate_hash(log_entry, prev_hash)
        log_entry["prev_hash"] = prev_hash
        log_entry["hash"] = log_hash

        self.logs.append(log_entry)
        self._save_logs()

        return log_hash

    def verify_integrity(self):
        if not self.logs:
            return True, None

        prev_hash = "0" * 64
        for index, log in enumerate(self.logs):
            expected_hash = self._calculate_hash(
                {k: v for k, v in log.items() if k not in ["prev_hash", "hash"]},
                prev_hash
            )

            if log["hash"] != expected_hash:
                return False, f"Hash inválido no log #{index}"

            if log["prev_hash"] != prev_hash:
                return False, f"Cadeia quebrada no log #{index}"

            prev_hash = log["hash"]

        return True, None

    def get_logs(self, limit=50, offset=0, user_id=None):
        logs = self.logs

        if user_id:
            logs = [log for log in logs if log.get('user_id') == user_id]

        logs = list(reversed(logs))
        return logs[offset:offset + limit]

    def get_total_logs(self, user_id=None):
        if user_id:
            return len([log for log in self.logs if log.get('user_id') == user_id])
        return len(self.logs)
