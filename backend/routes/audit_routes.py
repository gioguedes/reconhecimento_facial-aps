from flask import Blueprint, request, jsonify
from services.audit_service import AuditService
from models.user import UserResponse

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')
audit_service = AuditService()


@audit_bp.route('/logs', methods=['GET'])
def get_logs():
    """Retorna logs de auditoria com paginação"""
    try:
        # Extrair parâmetros
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        user_id = request.args.get('user_id', None, type=str)

        # Limitar range
        limit = min(limit, 100)  # Máximo 100 por vez
        offset = max(offset, 0)

        # Obter logs
        logs = audit_service.get_logs(limit=limit, offset=offset, user_id=user_id)
        total = audit_service.get_total_logs(user_id=user_id)

        # Verificar integridade
        is_valid, error_msg = audit_service.verify_integrity()

        return jsonify(UserResponse(
            success=True,
            message="Logs carregados com sucesso",
            data={
                "logs": logs,
                "total": total,
                "limit": limit,
                "offset": offset,
                "integrity_valid": is_valid,
                "integrity_error": error_msg if not is_valid else None
            }
        ).to_dict()), 200

    except Exception as e:
        return jsonify(UserResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        ).to_dict()), 500


@audit_bp.route('/verify-integrity', methods=['GET'])
def verify_integrity():
    """Verifica integridade da cadeia de logs"""
    try:
        is_valid, error_msg = audit_service.verify_integrity()
        total = audit_service.get_total_logs()

        return jsonify(UserResponse(
            success=True,
            message="Verificação concluída",
            data={
                "integrity_valid": is_valid,
                "total_logs": total,
                "error": error_msg
            }
        ).to_dict()), 200

    except Exception as e:
        return jsonify(UserResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        ).to_dict()), 500
