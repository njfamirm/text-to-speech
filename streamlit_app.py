import streamlit as st
from openai import OpenAI
import os
from pathlib import Path
from pydub import AudioSegment

# Initialize OpenAI API
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Function to detect leading silence
def milliseconds_until_sound(sound, silence_threshold_in_decibels=-20.0, chunk_size=10):
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold_in_decibels and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

# Function to trim start of audio
def trim_start(filepath):
    path = Path(filepath)
    directory = path.parent
    filename = path.name
    audio = AudioSegment.from_file(filepath, format="wav")
    start_trim = milliseconds_until_sound(audio)
    trimmed = audio[start_trim:]
    new_filename = directory / f"trimmed_{filename}"
    trimmed.export(new_filename, format="wav")
    return trimmed, new_filename

# Function to transcribe audio
def transcribe_audio(file,output_dir):
    audio_path = os.path.join(output_dir, file)
    with open(audio_path, 'rb') as audio_data:
        transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_data)
        return transcription.text

# Function to add punctuation
def punctuation_assistant(full_transcript):
    system_prompt = """You are a helpful assistant that adds punctuation to text and fix spelling mistakes in persian.
      Preserve the original words and only insert necessary punctuation such as periods,
      commas, capialization, symbols like dollar sings or percentage signs, and formatting.
      Avoid changing the words or sentence structure. If necessary, use a dictionary to identify ambiguous words."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": full_transcript
            }
        ]
    )
    return response

# Function to do custom things
def subject_assistant(full_transcript):
    system_prompt = """You are an intelligent assistant specialized in Shiite religious matters in persian:
    Preserve the original words
    Your task is to process religious speech texts to ensure all references to Shiite and religious matters are included and that the correct terms are used.
    - In front of the names of the Imams, you should use "(علیه‌السلام)" and similar phrases.
    - Arabic phrases such as Quranic verses and narrations may be used within the speech. Please write them with correct diacritics and place them inside «»."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": full_transcript
            }
        ]
    )
    return response

# Streamlit UI
st.title('Voice to Text Converter')

uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav"])
if uploaded_file is not None:
    # Save the uploaded file
    with open('uploaded_file.wav', 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    # Initialize the progress bar
    progress_bar = st.progress(0)

    # Process the uploaded file
    trimmed_audio, trimmed_filename = trim_start('uploaded_file.wav')
    progress_bar.progress(25)  # Update progress bar

    transcription = transcribe_audio(trimmed_filename, '.')
    progress_bar.progress(50)  # Update progress bar

    response = punctuation_assistant(transcription)
    punctuated_transcript = response.choices[0].message.content
    progress_bar.progress(75)  # Update progress bar

    response = subject_assistant(punctuated_transcript)
    final_transcript = response.choices[0].message.content
    progress_bar.progress(100)  # Update progress bar

    # Display the final transcript
    st.text_area("Text", value=final_transcript, height=200, max_chars=None)