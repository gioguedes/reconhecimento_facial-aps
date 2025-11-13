import base64
import cv2
import numpy as np
from typing import Tuple, Optional

def decode_base64_image(base64_string):
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        image_bytes = base64.b64decode(base64_string)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        return image
    except:
        return None

def encode_image_to_base64(image, format='.png'):
    try:
        success, buffer = cv2.imencode(format, image)
        if not success:
            return None

        image_base64 = base64.b64encode(buffer).decode('utf-8')
        mime_type = 'image/png' if format == '.png' else 'image/jpeg'
        return f"data:{mime_type};base64,{image_base64}"
    except:
        return None


def validate_image(image, min_size=(640, 480)):
    if image is None:
        return False, "Imagem inválida ou corrompida"

    height, width = image.shape[:2]
    min_width, min_height = min_size

    if width < min_width or height < min_height:
        return False, f"Imagem muito pequena ({width}x{height}). Mínimo: {min_width}x{min_height}"

    mean_brightness = np.mean(image)
    if mean_brightness < 10:
        return False, "Imagem muito escura"
    if mean_brightness > 245:
        return False, "Imagem muito clara"

    std_dev = np.std(image)
    if std_dev < 10:
        return False, "Imagem sem detalhes suficientes"

    return True, "OK"

def resize_image(image, target_size=(1280, 720)):
    height, width = image.shape[:2]
    target_width, target_height = target_size

    aspect = width / height
    target_aspect = target_width / target_height

    if aspect > target_aspect:
        new_width = target_width
        new_height = int(target_width / aspect)
    else:
        new_height = target_height
        new_width = int(target_height * aspect)

    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

def preprocess_image(image):
    # Equalização CLAHE
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    lab = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # Filtro bilateral
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
    return denoised
