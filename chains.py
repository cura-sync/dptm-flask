import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from prompts import *

# Load environment variables
load_dotenv()

# Define prompts
medicine_extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", MEDICINE_EXTRACTION_PROMPT),
    ("user", "Extract the medicines from the following prescription: {prescription}")
])

medicine_translation_prompt = ChatPromptTemplate.from_messages([
    ("system", MEDICINE_TRANSLATION_PROMPT),
    ("user", "Provide the salt profile of the following medicines: {medicines}")
])

translation_prompt = ChatPromptTemplate.from_messages([
    ("system", TRANSLATION_PROMPT),
    ("user", "Translate the following medical document to simpler language: {text}")
])

dosage_prompt = ChatPromptTemplate.from_messages([
    ("system", DOSAGE_PROMPT),
    ("user", "{text}")
])

audio_to_summary_prompt = ChatPromptTemplate.from_messages([
    ("system", AUDIO_TO_SUMMARY_PROMPT),
    ("user", "{text}")
])

llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo"
)

# Create chains
medicine_extraction_chain = medicine_extraction_prompt | llm
medicine_translation_chain = medicine_translation_prompt | llm
translation_chain = translation_prompt | llm
dosage_chain = dosage_prompt | llm
audio_to_summary_chain = audio_to_summary_prompt | llm