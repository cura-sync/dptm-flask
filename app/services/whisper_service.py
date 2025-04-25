import os
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

def transcribe_audio(audio_file) -> str:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    audio_file_path = os.getenv("DOCUMENT_LOCATION") + 'uploaded_audio/' + audio_file
    audio_file = open(audio_file_path, "rb")
    
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text",
    )

    return transcription