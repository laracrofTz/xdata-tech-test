import os, requests, subprocess
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "http://localhost:8001/asr"
AUDIO_DIR = "../../"
CSV_FILE = "./cv-valid-dev.csv"
# OUTPUT_CSV = "./cv-valid-dev-transcribed.csv"
AUD_OUT_PATH = "wav_audio"

MAX_WORKERS = 3

def mp3_to_wav(filename):
    cv_valid_dev_dir, mp3_file = filename.split("/")
    file = os.path.splitext(mp3_file)[0]
    input_path = os.path.join(AUDIO_DIR, filename)
    output_path = os.path.join(AUDIO_DIR, cv_valid_dev_dir, f"{file}.wav")

    try:
        subprocess.run(
            ["ffmpeg", "-i", input_path,
            "-ac", "1", "-ar", "16000",
            output_path, "-y"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"conversion failed for {filename}: {e}")

def transcribe_single_audio(filename):
    audio_filepath = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(audio_filepath):
        return {"filename": filename, "transcription": "File not found.", "duration": 0.0}

    try:
        with open(audio_filepath, "rb") as file:
            response = requests.post(API_URL, files={"file": file})
            if response.status_code == 200:
                return filename, response.json().get("transcription", "No transcription found."), response.json().get("duration", "0.0")
            else:
                return filename, f"error {response.status_code}", "0.0"
    except Exception as e:
        return filename, f"error: {str(e)}"

def process_audio_files():
    df = pd.read_csv(CSV_FILE)
    wav_audio_files = []

    if "generated_text" not in df.columns:
        df["generated_text"] = ""

    all_audio_files = df["filename"].tolist()
    df["filename"] = df["filename"].str.replace(".mp3", ".wav", regex=False) # convert filename into wav
    for mp3_audio in all_audio_files:
        mp3_to_wav(mp3_audio)
        wav_audio = mp3_audio.replace(".mp3", ".wav")
        wav_audio_files.append(wav_audio)

    # multi threading for parallel api calls to process them in a more optimised way
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {} # dictionary to keep track of the future instance and what file it corresponds to
        for file in wav_audio_files:
            future = executor.submit(transcribe_single_audio, file) # submit task to thread pool
            futures[future] = file
        for f in as_completed(futures):
            filename, transcription = f.result()
            df.loc[df["filename"]==filename, "generated_text"] = transcription

    df["filename"] = df["filename"].str.replace(".wav", ".mp3", regex=False)
    df.to_csv(CSV_FILE, index=False)
    print("transcription for the audio files are completed and saved to output csv")

process_audio_files()