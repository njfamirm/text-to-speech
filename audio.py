from pathlib import Path
from pydub import AudioSegment
from pydub.utils import mediainfo

# Function to detect leading silence
def milliseconds_until_sound(sound, silence_threshold_in_decibels=-20.0, chunk_size=10):
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold_in_decibels and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

# trim start of audio
def trim_start(filepath):
    path = Path(filepath)
    directory = path.parent
    filename = path.name
    file_format = mediainfo(filepath)['format_name']
    audio = AudioSegment.from_file(filepath, format=file_format)
    start_trim = milliseconds_until_sound(audio)
    trimmed = audio[start_trim:]
    new_filename = directory / f"trimmed-{filename}"
    trimmed.export(new_filename, format=file_format)
    return trimmed, new_filename