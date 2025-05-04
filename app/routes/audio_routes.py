from flask import Blueprint, request, jsonify
from app.services.whisper_service import transcribe_audio
from app.services.openai_service import ask_openai
from app.prompts.prompts import AUDIO_TO_SUMMARY_PROMPT
from app.nlp.preprocessor import process_extracted_text

audio_bp = Blueprint("audio_routes", __name__)

@audio_bp.route("/audio-to-summary", methods=["POST"])
def audio_to_summary():
    """
    Audio to Summary
    ---
    post:
      description: Transcribes an audio file and summarizes the conversation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                audio_file:
                  type: string
                  example: "audio1.mp3"
      responses:
        200:
          description: Audio summarized
    """
    data = request.json
    if not data or "audio_file" not in data:
        return jsonify({"error": "Missing audio_file field"}), 400

    audio_file = data["audio_file"]
    transcription = transcribe_audio(audio_file)
    processed_transcription = process_extracted_text(transcription)
    summary = ask_openai(AUDIO_TO_SUMMARY_PROMPT, transcription)

    return jsonify({
        "original_text": transcription,
        "summary": summary,
        "tokens_meta": {
            'pre_processing_tokens': len(transcription),
            'post_processing_tokens': len(processed_transcription)
        }
    }), 200