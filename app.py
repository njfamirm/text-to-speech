import logging
import streamlit as st
from audio import trim_start, split_audio
from os import getenv, path, remove
from openai_api import transcribe_audio, post_process_assistant
import hashlib
from openai import OpenAI
from datetime import datetime
import time

st_logger = logging.getLogger('streamlit')
st_logger.setLevel(logging.INFO)

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(layout="centered", page_title="Speech to text app", page_icon="🎙️")

class StreamlitHandler(logging.Handler):
    def __init__(self, log_area):
        super().__init__()
        self.log_area = log_area
        self.log_data = ""

    def emit(self, record):
        self.log_data += self.format(record) + "\n"
        self.log_area.empty()
        self.log_area.markdown(f"```\n{self.log_data}\n```")

def app():
  st.title('Speech to text app')

  with st.form(key='process_form'):

    default_openai_api_key = getenv('OPENAI_API_KEY')
    openai_api_key = st.text_input("OpenAI API Key", value=default_openai_api_key, type="password")
    uploaded_file = st.file_uploader("Upload your audio file", type=["wav", "mp3"])
    submit_button = st.form_submit_button(label='Process')

    log_area = st.empty()  # Placeholder for text_area update
    handler = StreamlitHandler(log_area)
    logger.addHandler(handler)

    if uploaded_file is not None:
      file_contents = uploaded_file.read()
      file_hash = hashlib.sha256(file_contents).hexdigest()[:8]
      file_extension = path.splitext(uploaded_file.name)[1]
      audio_filename = f'uploades/{file_hash}{file_extension}'

      with open(audio_filename, 'wb') as f:
        f.write(file_contents)

      logger.info('Audio file stored.')

      logger.info('Splitting audio...')
      file_names = split_audio(audio_filename)
      logger.info('Audio split.')

      client = OpenAI(api_key=openai_api_key)

      final_transcript = ""

      for index, filepath in enumerate(file_names):
        logger.info(f'Trimming audio chunk {index+1}...')
        trimmed_audio, trimmed_filename = trim_start(filepath)
        logger.info(f'Audio chunk {index+1} trimmed.')

        logger.info(f'Starting transcription of chunk {index+1}...')
        transcription = transcribe_audio(client, trimmed_filename)
        logger.info(f'Whisper Transcription of chunk {index+1} completed.')
        logger.info(transcription)

        logger.info(f'Starting post-process of chunk {index+1}...')
        response = post_process_assistant(client, transcription)
        punctuated_transcript = response.choices[0].message.content
        logger.info(f'Post-processed Transcription of chunk {index+1} completed.')
        logger.info(punctuated_transcript)

        final_transcript += punctuated_transcript + " "

        logger.info(f'Removing file {trimmed_filename}')
        remove(trimmed_filename)

      logger.info(f'Removing file {audio_filename}')
      remove(audio_filename)

      st.title('Final Transcript')
      st.code(final_transcript, language="txt")
      st.balloons()

  logger.info('App finished')

app()