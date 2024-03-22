import streamlit as st
from audio import trim_start
from os import getenv
from openai_api import transcribe_audio, punctuation_assistant, subject_assistant
import hashlib
from openai import OpenAI

def app():
  st.title('Audio Processing')

  with st.form(key='process_form'):
    default_openai_api_key = getenv('OPENAI_API_KEY')
    openai_api_key = st.text_input("OpenAI API Key", value=default_openai_api_key, type="password")
    uploaded_file = st.file_uploader("Upload your audio file", type=["wav", "mp3"])
    submit_button = st.form_submit_button(label='Process')

    if uploaded_file is not None:
      file_contents = uploaded_file.read()

      progress_bar = st.progress(0)

      file_hash = hashlib.sha256(file_contents).hexdigest()
      audio_filename = f'uploades/{file_hash}.wav'

      with open(audio_filename, 'wb') as f:
        f.write(file_contents)

      st.write('Audio file uploaded.')
      progress_bar.progress(5)

      st.write('Trimming audio...')
      client = OpenAI(api_key=openai_api_key)
      trimmed_audio, trimmed_filename = trim_start(audio_filename)
      st.write('Audio trimmed.')
      progress_bar.progress(25)

      st.write('Starting transcription...')
      transcription = transcribe_audio(client, trimmed_filename)
      st.write('Transcription completed.')
      progress_bar.progress(50)
      st.title('Whisper Transcription')
      st.code(transcription, language="txt")

      st.write('Starting punctuation...')
      response = punctuation_assistant(client, transcription)
      punctuated_transcript = response.choices[0].message.content
      st.write('Punctuation completed.')
      progress_bar.progress(75)
      st.title('Punctuated Transcription')
      st.code(punctuated_transcript, language="txt")

      st.write('Starting subject assistant...')
      response = subject_assistant(client, punctuated_transcript)
      final_transcript = response.choices[0].message.content
      st.write('Subject assistant completed.')
      progress_bar.progress(100)

      st.title('Final Transcript')
      st.code(final_transcript, language="txt")

app()