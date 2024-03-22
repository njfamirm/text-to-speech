from openai import OpenAI
import os

# Initialize OpenAI API
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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