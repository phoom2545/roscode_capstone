import os
import dotenv
import time
import requests
import speech_recognition as sr
from groq import Groq
import sys
import tty
import termios

# Suppress ALSA warnings
os.environ["ALSA_LOG_LEVEL"] = "none"

# Redirect stderr to suppress warnings
sys.stderr = open(os.devnull, 'w')

dotenv.load_dotenv()
BOTNOI_TOKEN = os.getenv("BOTNOI_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# API Endpoints
LLM_API_URL = "http://127.0.0.1:8002/generate"  # LLM with RAG
BOTNOI_TTS_URL = "https://api-voice.botnoi.ai/openapi/v1/generate_audio"

OUTPUT_DIR = "GeneratedAudio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for question...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=8)
            print("Processing...")

            # Save the audio to a temporary file
            audio_path = "temp.wav"
            with open(audio_path, "wb") as f:
                f.write(audio.get_wav_data())

            # Use Groq API for transcription
            with open(audio_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(audio_path, file.read()),
                    model="whisper-large-v3",
                    # prompt="Specify context or spelling",  # Optional
                    prompt="Transcribe English words clearly. Focus on technical terms.",
                    response_format="json",  # Optional
                    language="en",  # Change to "th" for Thai
                    temperature=0.0  # Optional
                )
                return transcription.text.strip()
        except sr.UnknownValueError:
            print("Could not understand speech")
        except sr.WaitTimeoutError:
            print("No input detected")
        except Exception as e:
            print(f"Error during transcription: {e}")
    return None

def query_llm(text):
    payload = {"query": text}
    headers = {"Content-Type": "application/json"}
    response = requests.post(LLM_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("response", "").strip()
    print(f"LLM Error: {response.text}")
    return None

def text_to_speech(text):
    headers = {"Botnoi-Token": BOTNOI_TOKEN, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "speaker": "2",
        "volume": 1.5,
        "speed": 0.9,
        "type_media": "wav",
        "save_file": "true",
    }
    response = requests.post(BOTNOI_TTS_URL, headers=headers, json=payload)

    if response.status_code == 200:
        audio_url = response.json().get("audio_url")
        if audio_url:
            audio_data = requests.get(audio_url).content
            audio_path = os.path.join(OUTPUT_DIR, "response_audio.wav")
            with open(audio_path, "wb") as file:
                file.write(audio_data)
            return audio_path
    print(f"TTS Error: {response.text}")
    return None

def play_audio(file_path):
    print("Playing audio...")
    os.system(f"aplay {file_path}")  # Use aplay for Linux or another audio player for your OS
    try:
        time.sleep(1)  # Small delay to ensure playback is fully stopped
        os.remove(file_path)
        print(f"Deleted {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

def get_key():
    """
    Reads a single key press from the terminal.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    print("Press SPACE to start talking, press X to exit.")
    time.sleep(1)  # Add a small delay to avoid false key press detection

    while True:
        print("Waiting for key press...")
        key = get_key()  # Wait for a key press
        if key == ' ':  # SPACE key pressed
            print("=== Conversation Started ===")
            while True:
                user_query = transcribe_audio()
                if user_query:
                    print(f"User: {user_query}")

                    llm_response = query_llm(user_query)
                    if llm_response:
                        print(f"Assistant: {llm_response}")

                        # Uncomment the following lines if you want to use TTS
                        # tts_audio = text_to_speech(llm_response)
                        # if tts_audio:
                        #     play_audio(tts_audio)
                    else:
                        print("LLM response failed.")
                else:
                    print("No speech detected.")

                print("Press X to end the conversation or SPACE to continue.")
                key = get_key()
                if key.lower() == 'x':  # X key pressed
                    print("=== Conversation Ended ===")
                    break
        elif key.lower() == 'x':  # X key pressed
            print("Exiting...")
            break

if __name__ == "__main__":
    main()