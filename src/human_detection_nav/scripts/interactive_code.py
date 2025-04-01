import os
import dotenv
import time
import requests
import speech_recognition as sr
from groq import Groq
import sys
import threading

# Suppress ALSA warnings
os.environ["ALSA_LOG_LEVEL"] = "none"

# Redirect stderr to suppress warnings
sys.stderr = open(os.devnull, 'w')

dotenv.load_dotenv()

class SpeechAssistant:
    def __init__(self):
        self.botnoi_token = os.getenv("BOTNOI_TOKEN")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.groq_api_key)
        self.llm_api_url = "http://127.0.0.1:8002/generate"
        self.botnoi_tts_url = "https://api-voice.botnoi.ai/openapi/v1/generate_audio"
        self.output_dir = "GeneratedAudio"
        os.makedirs(self.output_dir, exist_ok=True)
        self.should_stop = False  # Flag to indicate when to stop the assistant
        self.api_url = "http://172.16.0.200:5000"  # Flask API URL

    def check_button_state(self, button_type):
        """
        Check the state of a button from the Flask API.
        """
        try:
            response = requests.get(f"{self.api_url}/button")
            button_states = response.json()
            return button_states.get(button_type, False)
        except requests.exceptions.RequestException as e:
            print(f"Error checking button state: {e}")
            return False

    def transcribe_audio(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening for question...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=8)
                print("Processing...")
                audio_path = "temp.wav"
                with open(audio_path, "wb") as f:
                    f.write(audio.get_wav_data())
                with open(audio_path, "rb") as file:
                    transcription = self.client.audio.transcriptions.create(
                        file=(audio_path, file.read()),
                        model="whisper-large-v3",
                        prompt="Transcribe English words clearly. Focus on technical terms.",
                        response_format="json",
                        language="en",
                        temperature=0.0
                    )
                    return transcription.text.strip()
            except sr.UnknownValueError:
                print("Could not understand speech")
            except sr.WaitTimeoutError:
                print("No input detected")
            except Exception as e:
                print(f"Error during transcription: {e}")
        return None

    def query_llm(self, text):
        payload = {"query": text}
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.llm_api_url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        print(f"LLM Error: {response.text}")
        return None

    def text_to_speech(self, text):
        headers = {"Botnoi-Token": self.botnoi_token, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "speaker": "2",
            "volume": 1.5,
            "speed": 0.9,
            "type_media": "wav",
            "save_file": "true",
        }
        response = requests.post(self.botnoi_tts_url, headers=headers, json=payload)
        if response.status_code == 200:
            audio_url = response.json().get("audio_url")
            if audio_url:
                audio_data = requests.get(audio_url).content
                audio_path = os.path.join(self.output_dir, "response_audio.wav")
                with open(audio_path, "wb") as file:
                    file.write(audio_data)
                return audio_path
        print(f"TTS Error: {response.text}")
        return None

    def play_audio(self, file_path):
        print("Playing audio...")
        os.system(f"aplay {file_path}")
        try:
            time.sleep(1)
            os.remove(file_path)
            print(f"Deleted {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    def stop(self):
        """
        Stop the speech assistant and clean up resources.
        """
        self.should_stop = True
        print("Speech Assistant stopped.")

    def user_input(self,user_query):
        # Send what user spoke to the server.
    
        try:
            message = {"user_input": user_query}
            response = requests.post(f"{self.api_url}/user_input" ,json=message)
            if response.status_code == 200:
                print("User input sent to the server successfully.")
            else:
                print(f"Server returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending user input: {e}")

    def llm_answer(self,llm_response):
        # Send what user spoke to the server.
    
        try:
            message = {"llm_answer": llm_response}
            response = requests.post(f"{self.api_url}/llm_answer" ,json=message)
            if response.status_code == 200:
                print("LLM answer sent to the server successfully.")
            else:
                print(f"Server returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending llm answer: {e}")




    def run(self, timeout=None):
        """
        Main loop for the speech assistant.
        If a timeout is provided, the assistant will stop after the timeout period.
        """
        print("Speech Assistant is now active. Say something to start the conversation.")
        time.sleep(1)
        self.should_stop = False  # Reset the stop flag

        try:
            while not self.should_stop:
                # Check if the "interactive" button is pressed to stop the assistant
                if not self.check_button_state("interactive"):
                    print("Interactive button not pressed. Stopping Speech Assistant...")
                    self.should_stop = True
                    break

                user_query = self.transcribe_audio()
                if user_query:
                    print(f"User: {user_query}")
                    self.user_input(user_query)
                    
                    llm_response = self.query_llm(user_query)
                    if llm_response:
                        print(f"Assistant: {llm_response}")
                        self.llm_answer(llm_response)

                        # Uncomment the following lines if you want to use TTS
                        # tts_audio = self.text_to_speech(llm_response)
                        # if tts_audio:
                        #     self.play_audio(tts_audio)

                    else:
                        print("LLM response failed.")
                else:
                    print("No speech detected.")

        except Exception as e:
            print(f"Error in Speech Assistant: {e}")
        finally:
            self.stop()  # Ensure cleanup happens even if an error occurs