from flask import Blueprint, request, jsonify
from services.facial_recognition_service import FacialRecognitionService
from models.user import UserResponse

users_bp = Blueprint('users', __name__, url_prefix='/api/users')
facial_service = FacialRecognitionService()


@users_bp.route('', methods=['GET'])
def get_all_users():
    try:
        users = facial_service.get_all_users()

        return jsonify(UserResponse(
            success=True,
            message="Usuários carregados com sucesso",
            data={
                "users": users,
                "total": len(users)
            }
        ).to_dict()), 200

    except Exception as e:
        return jsonify(UserResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        ).to_dict()), 500


@users_bp.route('/<username>', methods=['DELETE'])
def delete_user(username):
    try:
        # Verificar se usuário existe
        if username not in facial_service.users:
            return jsonify(UserResponse(
                success=False,
                message="Usuário não encontrado",
                error=f"Usuário '{username}' não existe"
            ).to_dict()), 404

        # Remover usuário
        del facial_service.users[username]
        facial_service._save_users()

        # Remover MFA secret se existir
        facial_service.mfa_service.remove_secret(username)

        # Registrar no audit log
        facial_service.audit_service.add_log(
            event_type="user_deletion",
            user_id=username,
            decision="granted",
            reason=f"Usuário {username} foi deletado do sistema"
        )

        return jsonify(UserResponse(
            success=True,
            message="Usuário deletado com sucesso"
        ).to_dict()), 200

    except Exception as e:
        return jsonify(UserResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        ).to_dict()), 500


@users_bp.route('/<username>', methods=['GET'])
def get_user(username):
    try:
        # Verificar se usuário existe
        if username not in facial_service.users:
            return jsonify(UserResponse(
                success=False,
                message="Usuário não encontrado",
                error=f"Usuário '{username}' não existe"
            ).to_dict()), 404

        user = facial_service.users[username]

        return jsonify(UserResponse(
            success=True,
            message="Usuário encontrado",
            data={
                "name": user.name,
                "permission_level": user.permission_level,
                "enrolled_date": user.enrolled_date,
                "last_access": user.last_access,
                "requires_mfa": user.requires_mfa(),
                "failed_attempts": user.failed_attempts,
                "is_locked": user.is_locked_out()
            }
        ).to_dict()), 200

    except Exception as e:
        return jsonify(UserResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        ).to_dict()), 500
