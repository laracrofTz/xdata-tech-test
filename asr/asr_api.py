import os, subprocess
from flask import Flask, jsonify, request
import soundfile as sf

from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch

app = Flask(__name__)
port = int(os.environ.get('PORT', 8001))

# load asr model
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")

# TASK 2B, assume that asr_api.py is the main server file?
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"response": "pong"}), 200

# TASK 2C
@app.route('/asr', methods=["POST"])
def audio_transcription():
    if "file" not in request.files:
        return jsonify({"error": "No audio file provided."}), 400

    audio_in_path = "./mp3_audio"
    audio_out_path = "./wav_audio"

    mp3_file = request.files["file"]
    audio_filename = mp3_file.filename.split(".")[0]
    mp3_file.save(os.path.join(audio_in_path, mp3_file.filename))

    # convert mp3 to wav files + resampling to 16kHz
    try:
        subprocess.run(
            ["ffmpeg", "-i", f"{audio_in_path}/{mp3_file.filename}",
             "-ac", "1", "-ar", "16000",
             f"{audio_out_path}/{audio_filename}.wav", "-y"],
             check=True
        )

        audio, sample_rate = sf.read(f"{audio_out_path}/{audio_filename}.wav")

        input_values = processor(audio, return_tensors="pt", padding="longest").input_values
        logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)

        transcription = processor.batch_decode(predicted_ids)[0]
        duration = sf.info(f"{audio_out_path}/{audio_filename}.wav").duration

        return jsonify({"transcription": transcription, "duration": str(duration)})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "ffmpeg processing failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)