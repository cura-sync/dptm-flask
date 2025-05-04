from flask import Blueprint, request, jsonify
from app.services.azure_ocr_service import perform_ocr
from app.services.openai_service import ask_openai
from app.prompts.prompts import *
from app.nlp.preprocessor import process_extracted_text

ocr_bp = Blueprint("ocr_routes", __name__)

@ocr_bp.route("/test-route", methods=["POST"])
def test_route():
    """
    Test Route
    ---
    post:
      description: Test if the app is working
      responses:
        200:
          description: App is working
    """
    return jsonify({"message": "App working"})

@ocr_bp.route("/translate-prescription", methods=["POST"])
def translate_prescription():
    """
    Translate Prescription
    ---
    post:
      description: Extracts text from document and translates it into simple language
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                document_name:
                  type: string
                  example: "prescription1.jpg"
      responses:
        200:
          description: Translation completed
    """
    data = request.json
    if not data or "document_name" not in data:
        return jsonify({"error": "Missing document_name field"}), 400

    extracted_text = perform_ocr(data["document_name"])
    if not extracted_text:
        return jsonify({"error": "Failed to extract text from the document"}), 500

    processed_text = process_extracted_text(extracted_text)
    user_prompt = f"Translate the following medical document to simpler language: {processed_text}"
    translated_text = ask_openai(TRANSLATION_PROMPT, user_prompt)

    return jsonify({
        "original_text": extracted_text,
        "translated_prescription": translated_text,
        "tokens_meta": {
            'pre_processing_tokens': len(extracted_text),
            'post_processing_tokens': len(processed_text)
        }
    }), 200

@ocr_bp.route("/translate-prescription-with-medicine", methods=["POST"])
def translate_prescription_with_medicine():
    """
    Translate Prescription and Extract Medicine
    ---
    post:
      description: Translates prescription and extracts medicines and their salt profiles
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                document_name:
                  type: string
                  example: "prescription1.jpg"
      responses:
        200:
          description: Translation and medicine extraction completed
    """
    data = request.json
    if not data or "document_name" not in data:
        return jsonify({"error": "Missing document_name field"}), 400

    extracted_text = perform_ocr(data["document_name"])
    if not extracted_text:
        return jsonify({"error": "Failed to extract text from the document"}), 500

    processed_text = process_extracted_text(extracted_text)
    user_prompt_translation = f"Translate the following medical document to simpler language: {processed_text}"
    translated_prescription = ask_openai(TRANSLATION_PROMPT, user_prompt_translation)

    user_prompt_extraction = f"Extract the medicines from the following prescription: {processed_text}"
    extracted_medicines = ask_openai(MEDICINE_EXTRACTION_PROMPT, user_prompt_extraction)

    user_prompt_medicine_translation = f"Provide the salt profile of the following medicines: {extracted_medicines}"
    translated_medicine = ask_openai(MEDICINE_TRANSLATION_PROMPT, user_prompt_medicine_translation)

    return jsonify({
        "original_text": extracted_text,
        "translated_prescription": translated_prescription,
        "translated_medicine": translated_medicine,
        "tokens_meta": {
            'pre_processing_tokens': len(extracted_text),
            'post_processing_tokens': len(processed_text)
        }
    }), 200

@ocr_bp.route("/extract-dosage", methods=["POST"])
def extract_dosage():
    """
    Extract Dosage
    ---
    post:
      description: Extract dosage information from prescription
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                document_name:
                  type: string
                  example: "prescription1.jpg"
      responses:
        200:
          description: Dosage extracted
    """
    data = request.json
    if not data or "document_name" not in data:
        return jsonify({"error": "Missing document_name field"}), 400

    extracted_text = perform_ocr(data["document_name"])
    if not extracted_text:
        return jsonify({"error": "Failed to extract text from the document"}), 500

    processed_text = process_extracted_text(extracted_text)
    dosage_info = ask_openai(DOSAGE_PROMPT, processed_text)

    return jsonify({
        "original_text": extracted_text,
        "dosage": dosage_info,
        "tokens_meta": {
            'pre_processing_tokens': len(extracted_text),
            'post_processing_tokens': len(processed_text)
        }
    }), 200