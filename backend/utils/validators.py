import re

def validate_username(name):
    if not name or not name.strip():
        return False, "Nome vazio"

    name = name.strip()

    if len(name) < 2:
        return False, "Nome muito curto"
    if len(name) > 100:
        return False, "Nome muito longo"

    if not re.match(r'^[a-zA-ZÀ-ÿ0-9\s\-_]+$', name):
        return False, "Nome com caracteres inválidos"

    return True, "OK"

def validate_security_level(level):
    try:
        level_int = int(level)
    except (ValueError, TypeError):
        return False, "Nível inválido", 0

    if level_int not in [1, 2, 3]:
        return False, "Nível deve ser 1, 2 ou 3", 0

    return True, "OK", level_int

def validate_otp_code(code):
    if not code:
        return False, "Código vazio"

    code = code.strip()

    if not re.match(r'^\d{6}$', code):
        return False, "Código deve ter 6 dígitos"

    return True, "OK"

def validate_threshold(value):
    try:
        value_float = float(value)
    except (ValueError, TypeError):
        return False, "Threshold inválido", 0.0

    if value_float < 0.0 or value_float > 1.0:
        return False, "Threshold deve estar entre 0 e 1", 0.0

    return True, "OK", value_float
