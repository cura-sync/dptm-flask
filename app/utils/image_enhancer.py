# app/utils/image_enhancer.py

import cv2
import numpy as np
from PIL import Image
from io import BytesIO

def enhance_handwritten_image(image_path: str, save_debug: bool = False) -> BytesIO:
    """
    Enhance a prescription image (handwritten or printed) for Azure OCR.
    Applies grayscale, CLAHE, sharpening, resizing. Returns BytesIO stream under 4MB.
    """
    original = cv2.imread(image_path)
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)

    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(contrast, -1, kernel)

    height, width = sharpened.shape
    if height < 800:
        scale = 800 / height
        sharpened = cv2.resize(sharpened, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    if save_debug:
        cv2.imwrite("/mnt/data/debug_gray.jpg", gray)
        cv2.imwrite("/mnt/data/debug_clahe.jpg", contrast)
        cv2.imwrite("/mnt/data/debug_sharp.jpg", sharpened)

    # Compress image to keep size under 4MB
    pil_image = Image.fromarray(sharpened)
    buffer = BytesIO()
    quality = 95
    while True:
        buffer.seek(0)
        buffer.truncate()
        pil_image.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() < 4 * 1024 * 1024 or quality <= 20:
            break
        quality -= 5

    buffer.seek(0)
    return buffer