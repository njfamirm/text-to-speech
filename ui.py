import streamlit as st
from audio import trim_start
from openai import transcribe_audio, punctuation_assistant, subject_assistant
import hashlib

st.title('Voice to Text Converter')

uploaded_file = st.file_uploader("Upload your audio file", type=["wav"])
if uploaded_file is not None:
    file_contents = uploaded_file.read()
    
    # Generate a hash of the file contents
    file_hash = hashlib.sha256(file_contents).hexdigest()
    unique_filename = file_hash + '.wav'

    # Save the uploaded file
    with open(unique_filename, 'wb') as f:
        f.write(f'uploades/{file_contents}')
    
    # Initialize the progress bar
    progress_bar = st.progress(0)

    # Process the uploaded file
    trimmed_audio, trimmed_filename = trim_start(unique_filename)
    progress_bar.progress(25)

    transcription = transcribe_audio(trimmed_filename, '.')
    progress_bar.progress(50)

    response = punctuation_assistant(transcription)
    punctuated_transcript = response.choices[0].message.content
    progress_bar.progress(75)

    response = subject_assistant(punctuated_transcript)
    final_transcript = response.choices[0].message.content
    progress_bar.progress(100)

    # Display the final transcript
    st.text_area("Text", value=final_transcript, height=200, max_chars=None)
else:
    st.write('Please upload an audio file to get started.')