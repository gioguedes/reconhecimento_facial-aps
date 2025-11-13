from flask import Blueprint, request, jsonify
from utils.validators import validate_username, validate_security_level, validate_otp_code
from utils.image_utils import decode_base64_image, validate_image
from services.facial_recognition_service import FacialRecognitionService
from models.user import UserResponse

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
facial_service = FacialRecognitionService()


@auth_bp.route('/enroll', methods=['POST'])
def enroll_user():
    """Cadastra um novo usuário no sistema através de reconhecimento facial"""
    try:
        if not request.json:
            return jsonify(UserResponse(
                success=False,
                message="Requisição inválida",
                error="Corpo da requisição deve ser JSON"
            ).to_dict()), 400

        name = request.json.get('name', '').strip()
        security_level = request.json.get('security_level')
        image_base64 = request.json.get('image')

        is_valid, message = validate_username(name)
        if not is_valid:
            return jsonify(UserResponse(
                success=False,
                message="Nome inválido",
                error=message
            ).to_dict()), 400

        is_valid, message, level = validate_security_level(security_level)
        if not is_valid:
            return jsonify(UserResponse(
                success=False,
                message="Nível de segurança inválido",
                error=message
            ).to_dict()), 400

        if not image_base64:
            return jsonify(UserResponse(
                success=False,
                message="Imagem não fornecida",
                error="Campo 'image' é obrigatório"
            ).to_dict()), 400

        image = decode_base64_image(image_base64)
        if image is None:
            return jsonify(UserResponse(
                success=False,
                message="Erro ao processar imagem",
                error="Imagem inválida ou corrompida"
            ).to_dict()), 400

        is_valid, message = validate_image(image)
        if not is_valid:
            return jsonify(UserResponse(
                success=False,
                message="Imagem não atende aos requisitos",
                error=message
            ).to_dict()), 400

        success, msg, qr_code = facial_service.enroll_user(name, level, image)

        if not success:
            return jsonify(UserResponse(
                success=False,
                message="Falha no cadastro",
                error=msg
            ).to_dict()), 400

        response_data = {"requires_mfa": level >= 2}
        if qr_code:
            response_data["qr_code"] = qr_code

        return jsonify(UserResponse(
            success=True,
            message=msg,
            data=response_data
        ).to_dict()), 201

    except Exception as e:
        return jsonify(UserResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        ).to_dict()), 500


@auth_bp.route('/authenticate', methods=['POST'])
def authenticate_user():
    """Realiza autenticação do usuário através de reconhecimento facial"""
    try:
        # Validar JSON
        if not request.json:
            return jsonify(UserResponse(
                success=False,
                message="Requisição inválida",
                error="Corpo da requisição deve ser JSON"
            ).to_dict()), 400

        # Extrair imagem
        image_base64 = request.json.get('image')

        if not image_base64:
            return jsonify(UserResponse(
                success=False,
                message="Imagem não fornecida",
                error="Campo 'image' é obrigatório"
            ).to_dict()), 400

        # Decodificar imagem
        image = decode_base64_image(image_base64)
        if image is None:
            return jsonify(UserResponse(
                success=False,
                message="Erro ao processar imagem",
                error="Imagem inválida ou corrompida"
            ).to_dict()), 400

        # Autenticar
        success, username, level, confidence, requires_mfa, msg = facial_service.authenticate_user(image)

        if not success:
            return jsonify(UserResponse(
                success=False,
                message=msg,
                error="Falha na autenticação"
            ).to_dict()), 401

        # Preparar resposta
        response_data = {
            "user": username,
            "permission_level": level,
            "confidence": round(confidence, 4),
            "requires_mfa": requires_mfa
        }

        return jsonify(UserResponse(
            success=True,
            message=msg,
            data=response_data
        ).to_dict()), 200

    except Exception as e:
        return jsonify(UserResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        ).to_dict()), 500


@auth_bp.route('/verify-mfa', methods=['POST'])
def verify_mfa():
    """Valida código de autenticação de dois fatores e libera acesso ao sistema"""
    try:
        # Validar JSON
        if not request.json:
            return jsonify(UserResponse(
                success=False,
                message="Requisição inválida",
                error="Corpo da requisição deve ser JSON"
            ).to_dict()), 400

        # Extrair dados
        username = request.json.get('username', '').strip()
        otp_code = request.json.get('otp_code', '').strip()

        # Validar nome
        is_valid, message = validate_username(username)
        if not is_valid:
            return jsonify(UserResponse(
                success=False,
                message="Nome inválido",
                error=message
            ).to_dict()), 400

        # Validar código OTP
        is_valid, message = validate_otp_code(otp_code)
        if not is_valid:
            return jsonify(UserResponse(
                success=False,
                message="Código OTP inválido",
                error=message
            ).to_dict()), 400

        # Verificar MFA
        success, msg = facial_service.verify_mfa_and_grant_access(username, otp_code)

        if not success:
            return jsonify(UserResponse(
                success=False,
                message=msg,
                error="Falha na verificação MFA"
            ).to_dict()), 401

        return jsonify(UserResponse(
            success=True,
            message=msg
        ).to_dict()), 200

    except Exception as e:
        return jsonify(UserResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        ).to_dict()), 500
