import streamlit as st
from audio import trim_start, split_audio
from os import getenv, path
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

      file_hash = hashlib.sha256(file_contents).hexdigest()[:8]
      file_extension = path.splitext(uploaded_file.name)[1]
      audio_filename = f'uploades/{file_hash}{file_extension}'

      with open(audio_filename, 'wb') as f:
        f.write(file_contents)

      st.write('Audio file uploaded.')
      progress_bar.progress(5)

      st.write('Splitting audio...')
      file_names = split_audio(audio_filename)
      st.write('Audio split.')
      progress_bar.progress(10)

      client = OpenAI(api_key=openai_api_key)

      final_transcript = ""

      for filepath in file_names:
        st.write(f'Trimming audio chunk {filepath}...')
        trimmed_audio, trimmed_filename = trim_start(filepath)
        st.write(f'Audio chunk {filepath} trimmed.')
        progress_bar.progress(25)

        st.write(f'Starting transcription of chunk {filepath}...')
        transcription = transcribe_audio(client, trimmed_filename)
        st.write(f'Transcription of chunk {filepath} completed.')
        progress_bar.progress(50)
        st.title(f'Whisper Transcription of chunk {filepath}')
        st.code(transcription, language="txt")

        st.write(f'Starting punctuation of chunk {filepath}...')
        response = punctuation_assistant(client, transcription)
        punctuated_transcript = response.choices[0].message.content
        st.write(f'Punctuation of chunk {filepath} completed.')
        progress_bar.progress(75)
        st.title(f'Punctuated Transcription of chunk {filepath}')
        st.code(punctuated_transcript, language="txt")

        st.write(f'Starting subject assistant of chunk {filepath}...')
        response = subject_assistant(client, punctuated_transcript)
        chunk_final_transcript = response.choices[0].message.content
        st.write(f'Subject assistant of chunk {filepath} completed.')
        progress_bar.progress(100)

        st.title(f'Final Transcript of chunk {filepath}')
        st.code(chunk_final_transcript, language="txt")

        final_transcript += chunk_final_transcript + " "

      st.title('Final Transcript')
      st.code(final_transcript, language="txt")

      st.balloons()

app()