"""
This service is used to perform OCR on an image using Azure Computer Vision.
It enhances the image and then performs OCR on the enhanced image.
"""

import os
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from app.utils.image_enhancer import enhance_handwritten_image

def perform_ocr(document_name: str) -> str:
    COMPUTER_VISION_KEY = os.getenv("CV_KEY")
    COMPUTER_VISION_ENDPOINT = os.getenv("CV_ENDPOINT")
    DOCUMENT_ROOT_PATH = os.getenv("DOCUMENT_LOCATION")

    image_path = DOCUMENT_ROOT_PATH + "uploaded_documents/" + document_name
    enhanced_image = enhance_handwritten_image(image_path, save_debug=True)

    computervision_client = ComputerVisionClient(
        COMPUTER_VISION_ENDPOINT,
        CognitiveServicesCredentials(COMPUTER_VISION_KEY)
    )

    read_response = computervision_client.read_in_stream(enhanced_image, raw=True)
    operation_id = read_response.headers["Operation-Location"].split("/")[-1]

    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower() not in ['notstarted', 'running']:
            break
        time.sleep(1)

    if read_result.status == OperationStatusCodes.succeeded:
        extracted_text = []
        for page in read_result.analyze_result.read_results:
            for line in page.lines:
                extracted_text.append(line.text)
        return "\n".join(extracted_text)
    else:
        return None