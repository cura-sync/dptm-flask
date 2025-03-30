from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from PIL import Image
import time
import os
import re
import json
from dotenv import load_dotenv
load_dotenv()
from typing import List, Sequence
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph
from chains import *
from whisper import transcribe_audio

app = Flask(__name__)
CORS(app)

MEDICINE_EXTRACTION = "medicine_extraction"
MEDICINE_TRANSLATION = "medicine_translation"

def perform_ocr(document_name: str) -> str:
    COMPUTER_VISION_KEY = os.getenv("CV_KEY")
    COMPUTER_VISION_ENDPOINT = os.getenv("CV_ENDPOINT")
    DOCUMENT_ROOT_PATH = os.getenv("DOCUMENT_LOCATION")

    computervision_client = ComputerVisionClient(COMPUTER_VISION_ENDPOINT, CognitiveServicesCredentials(COMPUTER_VISION_KEY))
    with open(DOCUMENT_ROOT_PATH + "uploaded_documents/" + document_name, "rb") as image:
        read_response = computervision_client.read_in_stream(image, raw=True)

    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower() not in ['notstarted', 'running']:
            break
        time.sleep(1)


    if read_result.status == OperationStatusCodes.succeeded:
        extracted_text = []  # Initialize a list to collect the text
        for page in read_result.analyze_result.read_results:
            for line in page.lines:
                extracted_text.append(line.text)  # Collect the text
        return "\n".join(extracted_text)  # Return the collected text as a single string
    else:
        return None

def medicine_extraction_node(state: Sequence[BaseMessage]) -> List[BaseMessage]:
    return medicine_extraction_chain.invoke({"prescription": state})

def medicine_translation_node(state: Sequence[BaseMessage]) -> List[BaseMessage]:
    result = medicine_translation_chain.invoke({"medicines": state})
    if isinstance(result, str):
        return [HumanMessage(content=result)]
    else:
        return [HumanMessage(content=str(result))]  # Convert to string if necessary

builder = MessageGraph()
builder.add_node(MEDICINE_EXTRACTION, medicine_extraction_node)
builder.add_node(MEDICINE_TRANSLATION, medicine_translation_node)
builder.set_entry_point(MEDICINE_EXTRACTION)
builder.add_edge(MEDICINE_EXTRACTION, MEDICINE_TRANSLATION)
builder.add_edge(MEDICINE_TRANSLATION, END)
graph = builder.compile()

@app.route("/test-route", methods=["POST"])
def test_route():
    return jsonify({"message": "App working"})

@app.route("/translate-prescription", methods=["POST"])
def translate_prescription():
    data = request.json
    if not data or "document_name" not in data:
        return jsonify({"error": "Missing document_name field"}), 400
    
    extracted_text = perform_ocr(data["document_name"])
    if not extracted_text:
        return jsonify({"error": "Failed to extract text from the document"}), 500
    
    inputs = HumanMessage(content=extracted_text)
    response = translation_chain.invoke(inputs)
    return jsonify({
        "original_text": extracted_text,
        "translated_prescription": response.content
    }), 200

@app.route("/translate-prescription-with-medicine", methods=["POST"])
def translate_prescription_with_medicine():
    data = request.json
    if not data or "document_name" not in data:
        return jsonify({"error": "Missing document_name field"}), 400
    
    extracted_text = perform_ocr(data["document_name"])
    if not extracted_text:
        return jsonify({"error": "Failed to extract text from the document"}), 500
    
    inputs = HumanMessage(content=extracted_text)

    response_prescription_translation = translation_chain.invoke(inputs)
    response_salt_analysis = graph.invoke(inputs)

    if not response_salt_analysis:
        return jsonify({"error": "Failed to extract medicine from the prescription"}), 500
    
    if not response_prescription_translation:
        return jsonify({"error": "Failed to translate the prescription"}), 500
    
    response_salt_analysis = response_salt_analysis[-1].content.split("content=", 1)[-1].split("' additional_kwargs=")[0]

    return jsonify({
        "original_text": extracted_text,
        "translated_prescription": response_prescription_translation.content,
        "translated_medicine": response_salt_analysis
    }), 200

@app.route("/extract-dosage", methods=["POST"])
def extract_dosage():
    data = request.json
    if not data or "document_name" not in data:
        return jsonify({"error": "Missing document_name field"}), 400
    
    extracted_text = perform_ocr(data["document_name"])
    if not extracted_text:
        return jsonify({"error": "Failed to extract text from the document"}), 500

    inputs = HumanMessage(content=extracted_text)
    response = dosage_chain.invoke(inputs)

    return jsonify({
        "original_text": extracted_text,
        "dosage": response.content
    }), 200

@app.route("/audio-to-summary", methods=["POST"])
def audio_to_summary():
    data = request.json
    if not data or "audio_file" not in data:
        return jsonify({"error": "Missing audio_file field"}), 400
    
    audio_file = data["audio_file"]
    transcription = transcribe_audio(audio_file)
    response = audio_to_summary_chain.invoke(transcription)

    return jsonify({
        "original_text": transcription,
        "summary": response.content
    }), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000, debug=True)
