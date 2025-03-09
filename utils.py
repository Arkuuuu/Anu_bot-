import os
import requests
from dotenv import load_dotenv
import base64
import streamlit as st
import boto3

load_dotenv()
api_key = os.getenv("groq_api_key")
# Base URL per Groq documentation; override via .env if needed.
BASE_URL = os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1")

def get_answer(messages):
    """
    Uses Groq's chat completions endpoint to get an answer.
    Endpoint: POST {BASE_URL}/chat/completions
    """
    headers = {
         "Authorization": f"Bearer {api_key}",
         "Content-Type": "application/json"
    }
    data = {
         "messages": messages,
         "model": "llama-3.3-70b-versatile"  # Update with your desired Groq model.
         # Optional parameters like temperature, top_p, etc., can be added here.
    }
    response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    response_json = response.json()
    return response_json["choices"][0]["message"]["content"].strip()

def speech_to_text(audio_data):
    """
    Uses Groq's audio transcriptions endpoint to convert speech to text.
    Endpoint: POST {BASE_URL}/audio/transcriptions
    """
    headers = {
         "Authorization": f"Bearer {api_key}"
    }
    with open(audio_data, "rb") as f:
         file_content = f.read()
    files = {
         "file": (audio_data, file_content)
    }
    data = {
         "model": "whisper-large-v3",
         "response_format": "json",
         "language": "en",
         "temperature": 0.0
    }
    response = requests.post(f"{BASE_URL}/audio/transcriptions", headers=headers, data=data, files=files)
    response.raise_for_status()
    return response.json()["text"]

def text_to_speech(input_text):
    """
    Uses Amazon Polly to convert text to speech.
    
    Ensure AWS credentials are configured (e.g., via environment variables or AWS config file).
    """
    polly_client = boto3.client('polly')
    response = polly_client.synthesize_speech(
        Text=input_text,
        OutputFormat='mp3',
        VoiceId='Joanna'  # Change this voice if desired.
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        f.write(response['AudioStream'].read())
    return webm_file_path

def autoplay_audio(file_path: str):
    """
    Encodes the audio file in base64 and renders an HTML audio element to play it.
    """
    with open(file_path, "rb") as f:
         data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
      <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
