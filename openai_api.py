import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# transcribe audio
def transcribe_audio(client, audio_path):
  with open(audio_path, 'rb') as audio_data:
    logger.info('Starting transcription...')
    transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_data, language="fa", prompt='')
    logger.info('Transcription completed.')
    return transcription.text

# post-process assistant
def post_process_assistant(client, full_transcript):
  system_prompt = """You are a helpful assistant that adds punctuation to Persian text, corrects spelling mistakes, and ensures proper religious references for Shiite matters.
    You are familiar with the grammar, punctuation rules of the Persian language, and Arabic phrases commonly used in Shiite discourse. 
    Preserve the original words and only insert necessary punctuation such as periods, commas, capitalization, symbols like Rial signs or percentage signs, and formatting. 
    - When referring to the names of the Imams, you should use "(علیه‌السلام)" and similar phrases.
    - Arabic phrases such as Quranic verses and narrations may be used within the speech. Please write them with correct diacritics.
    Avoid changing the words or sentence structure. If necessary, use a Persian dictionary to identify ambiguous words. 
    Your goal is to make the text as clear and readable as possible while maintaining its original meaning and religious context."""
  logger.info('Starting punctuation...')
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
  logger.info('Post-process completed.')
  return response
