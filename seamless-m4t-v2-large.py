# https://huggingface.co/facebook/seamless-m4t-v2-large

import torch
from transformers import Wav2Vec2ForCTC, AutoProcessor, pipeline

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "facebook/seamless-m4t-v2-large"

model = Wav2Vec2ForCTC.from_pretrained(
    model_id, torch_dtype=torch_dtype
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)

result = pipe("voice_01.wav")
print(result["text"])