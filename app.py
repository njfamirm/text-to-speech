import logging
import streamlit as st
from audio import trim_start, split_audio
from os import getenv, path, remove
from openai_api import transcribe_audio, punctuation_assistant, subject_assistant
import hashlib
from openai import OpenAI

st_logger = logging.getLogger('streamlit')
st_logger.setLevel(logging.DEBUG)

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(layout="centered", page_title="Speech to text app", page_icon="🎙️")

def app():
  logger.info('Starting app')
  st.title('Speech to text app')

  with st.form(key='process_form'):
    progress_bar = st.progress(0)

    default_openai_api_key = getenv('OPENAI_API_KEY')
    openai_api_key = st.text_input("OpenAI API Key", value=default_openai_api_key, type="password")
    uploaded_file = st.file_uploader("Upload your audio file", type=["wav", "mp3"])
    submit_button = st.form_submit_button(label='Process')

    if uploaded_file is not None:
      file_contents = uploaded_file.read()
      file_hash = hashlib.sha256(file_contents).hexdigest()[:8]
      file_extension = path.splitext(uploaded_file.name)[1]
      audio_filename = f'uploades/{file_hash}{file_extension}'

      with open(audio_filename, 'wb') as f:
        f.write(file_contents)

      logger.info('Audio file stored.')
      st.write('Audio file stored.')
      progress_bar.progress(5)

      logger.info('Splitting audio...')
      st.write('Splitting audio...')
      file_names = split_audio(audio_filename)
      logger.info('Audio split.')
      st.write('Audio split.')
      progress_bar.progress(10)

      client = OpenAI(api_key=openai_api_key)

      final_transcript = ""

      for index, filepath in enumerate(file_names):
        logger.info(f'Trimming audio chunk {index+1}...')
        st.write(f'Trimming audio chunk {index+1}...')
        trimmed_audio, trimmed_filename = trim_start(filepath)
        logger.info(f'Audio chunk {index+1} trimmed.')
        st.write(f'Audio chunk {index+1} trimmed.')
        progress_bar.progress(25)

        logger.info(f'Starting transcription of chunk {index+1}...')
        st.write(f'Starting transcription of chunk {index+1}...')
        transcription = transcribe_audio(client, trimmed_filename)
        logger.info(f'Transcription of chunk {index+1} completed.')
        st.write(f'Transcription of chunk {index+1} completed.')
        progress_bar.progress(50)
        st.title(f'Whisper Transcription of chunk {index+1}')
        st.code(transcription, language="txt")

        logger.info(f'Starting punctuation of chunk {index+1}...')
        st.write(f'Starting punctuation of chunk {index+1}...')
        response = punctuation_assistant(client, transcription)
        punctuated_transcript = response.choices[0].message.content
        logger.info(f'Punctuation of chunk {index+1} completed.')
        st.write(f'Punctuation of chunk {index+1} completed.')
        progress_bar.progress(75)
        st.title(f'Punctuated Transcription of chunk {index+1}')
        st.code(punctuated_transcript, language="txt")

        logger.info(f'Starting subject assistant of chunk {index+1}...')
        st.write(f'Starting subject assistant of chunk {index+1}...')
        response = subject_assistant(client, punctuated_transcript)
        chunk_final_transcript = response.choices[0].message.content
        logger.info(f'Subject assistant of chunk {index+1} completed.')
        st.write(f'Subject assistant of chunk {index+1} completed.')
        progress_bar.progress(100)

        st.title(f'Final Transcript of chunk {index+1}')
        st.code(chunk_final_transcript, language="txt")

        final_transcript += chunk_final_transcript + " "

        logger.info(f'Removing file {trimmed_filename}')
        remove(trimmed_filename)

      st.title('Final Transcript')
      st.code(final_transcript, language="txt")
      st.balloons()

      logger.info(f'Removing file {audio_filename}')
      remove(audio_filename)

  logger.info('App finished')

app()