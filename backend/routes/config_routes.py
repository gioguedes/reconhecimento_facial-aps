from flask import Blueprint, request, jsonify
from utils.validators import validate_threshold
from services.facial_recognition_service import FacialRecognitionService
from models.user import UserResponse

config_bp = Blueprint('config', __name__, url_prefix='/api/config')
facial_service = FacialRecognitionService()


@config_bp.route('', methods=['GET'])
def get_config():
    """Retorna configurações atuais dos thresholds"""
    try:
        thresholds = facial_service.thresholds

        return jsonify(UserResponse(
            success=True,
            message="Configurações carregadas",
            data={
                "nivel_1_threshold": thresholds[1],
                "nivel_2_threshold": thresholds[2],
                "nivel_3_threshold": thresholds[3]
            }
        ).to_dict()), 200

    except Exception as e:
        return jsonify(UserResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        ).to_dict()), 500


@config_bp.route('', methods=['PUT'])
def update_config():
    """Atualiza thresholds de confiança"""
    try:
        # Validar JSON
        if not request.json:
            return jsonify(UserResponse(
                success=False,
                message="Requisição inválida",
                error="Corpo da requisição deve ser JSON"
            ).to_dict()), 400

        # Extrair e validar thresholds
        level_1 = request.json.get('nivel_1_threshold')
        level_2 = request.json.get('nivel_2_threshold')
        level_3 = request.json.get('nivel_3_threshold')

        # Validar cada threshold
        is_valid_1, msg_1, value_1 = validate_threshold(level_1)
        is_valid_2, msg_2, value_2 = validate_threshold(level_2)
        is_valid_3, msg_3, value_3 = validate_threshold(level_3)

        if not is_valid_1:
            return jsonify(UserResponse(
                success=False,
                message="Threshold nível 1 inválido",
                error=msg_1
            ).to_dict()), 400

        if not is_valid_2:
            return jsonify(UserResponse(
                success=False,
                message="Threshold nível 2 inválido",
                error=msg_2
            ).to_dict()), 400

        if not is_valid_3:
            return jsonify(UserResponse(
                success=False,
                message="Threshold nível 3 inválido",
                error=msg_3
            ).to_dict()), 400

        # Validar ordem lógica (nível 3 >= nível 2 >= nível 1)
        if not (value_1 <= value_2 <= value_3):
            return jsonify(UserResponse(
                success=False,
                message="Ordem inválida",
                error="Thresholds devem seguir a ordem: Nível 1 <= Nível 2 <= Nível 3"
            ).to_dict()), 400

        # Atualizar thresholds
        success, msg = facial_service.update_thresholds(value_1, value_2, value_3)

        if not success:
            return jsonify(UserResponse(
                success=False,
                message="Falha ao atualizar",
                error=msg
            ).to_dict()), 500

        return jsonify(UserResponse(
            success=True,
            message=msg,
            data={
                "nivel_1_threshold": value_1,
                "nivel_2_threshold": value_2,
                "nivel_3_threshold": value_3
            }
        ).to_dict()), 200

    except Exception as e:
        return jsonify(UserResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        ).to_dict()), 500
