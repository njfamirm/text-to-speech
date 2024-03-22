import streamlit as st
from audio import trim_start
from openai_api import transcribe_audio, punctuation_assistant, subject_assistant
import hashlib
from openai import OpenAI

st.title('Voice to Text Converter')

openai_api_key = st.sidebar.text_input("OpenAI API Key", value="", type="password")
client = OpenAI(api_key=openai_api_key)

uploaded_file = st.file_uploader("Upload your audio file", type=["wav"])
if uploaded_file is not None:
    file_contents = uploaded_file.read()
    
    # Generate a hash of the file contents
    file_hash = hashlib.sha256(file_contents).hexdigest()
    audio_filename = f'uploades/{file_hash}.wav'

    # Save the uploaded file
    with open(audio_filename, 'wb') as f:
        f.write(file_contents)
    
    # Initialize the progress bar
    progress_bar = st.progress(0)

    # Process the uploaded file
    trimmed_audio, trimmed_filename = trim_start(audio_filename)
    progress_bar.progress(25)

    transcription = transcribe_audio(client, trimmed_filename)
    progress_bar.progress(50)

    response = punctuation_assistant(client, transcription)
    punctuated_transcript = response.choices[0].message.content
    progress_bar.progress(75)

    response = subject_assistant(client, punctuated_transcript)
    final_transcript = response.choices[0].message.content
    progress_bar.progress(100)

    # Display the final transcript
    st.text_area("Text", value=final_transcript, height=200, max_chars=None)
else:
    st.write('Please upload an audio file to get started.')