from flask import Blueprint, jsonify
from services.audit_service import AuditService

health_bp = Blueprint('health', __name__, url_prefix='/api')
audit_service = AuditService()


@health_bp.route('/', methods=['GET'])
@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do sistema"""
    is_valid, error_msg = audit_service.verify_integrity()

    return jsonify({
        "status": "ok",
        "message": "Sistema de reconhecimento facial operacional",
        "integrity_check": "passed" if is_valid else "failed",
        "integrity_error": error_msg if not is_valid else None
    }), 200
