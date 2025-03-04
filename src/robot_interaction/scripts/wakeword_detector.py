# wakeword_detector.py
import speech_recognition as sr
import time

class WakewordDetector:
    def __init__(self, wakeword="hey lisa", listen_timeout=10, process_timeout=5):
        self.recognizer = sr.Recognizer()
        self.wakeword = wakeword.lower()
        self.listen_timeout = listen_timeout  # Timeout for initial listening
        self.process_timeout = process_timeout  # Timeout after hearing speech
        
    def detect_wakeword(self):
        """
        Listen for the wakeword with a two-phase timeout approach.
        
        Returns:
            int: 1 if wakeword detected, 0 if no speech detected, -1 if speech detected but no wakeword
        """
        try:
            with sr.Microphone() as source:
                print(f"Listening for wakeword for {self.listen_timeout} seconds...")
                self.recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
                
                # Phase 1: Wait for initial speech
                try:
                    print("Waiting for speech...")
                    audio = self.recognizer.listen(source, timeout=self.listen_timeout)
                    print(f"Speech detected! Processing for {self.process_timeout} seconds...")
                    
                    # Phase 2: Process the speech and continue listening for a short time
                    start_time = time.time()
                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                        print(f"Detected speech: {text}")
                        
                        # Check if wakeword is in the detected speech
                        if self.wakeword in text:
                            print("Wakeword detected!")
                            return 1  # Wakeword detected
                        
                        # If not, continue listening for the remaining time
                        remaining_time = self.process_timeout - (time.time() - start_time)
                        if remaining_time > 0:
                            print(f"Wakeword not found. Continuing to listen for {remaining_time:.1f} more seconds...")
                            try:
                                audio = self.recognizer.listen(source, timeout=remaining_time)
                                text = self.recognizer.recognize_google(audio).lower()
                                print(f"Additional speech detected: {text}")
                                
                                if self.wakeword in text:
                                    print("Wakeword detected in follow-up!")
                                    return 1  # Wakeword detected
                                else:
                                    print("Wakeword not detected in follow-up.")
                                    return -1  # Speech detected but no wakeword
                            except (sr.WaitTimeoutError, sr.UnknownValueError):
                                print("No additional speech detected.")
                                return -1  # Speech detected but no wakeword
                        else:
                            return -1  # Speech detected but no wakeword
                    
                    except sr.UnknownValueError:
                        print("Could not understand initial audio")
                        return -1  # Speech detected but couldn't be understood
                
                except sr.WaitTimeoutError:
                    print(f"No speech detected within {self.listen_timeout} seconds timeout")
                    return 0  # No speech detected
                    
        except Exception as e:
            print(f"An error occurred: {e}")
            return -1  # Error occurred
        
        return -1  # Default fallback

# For testing the module independently
if __name__ == "__main__":
    detector = WakewordDetector(listen_timeout=10, process_timeout=5)
    print("Starting wakeword detection...")
    
    while True:
        result = detector.detect_wakeword()
        if result == 1:
            print("Wakeword detected! Performing action...")
            break  # Exit the loop after detecting the wakeword
        elif result == 0:
            print("No speech detected. Listening again...")
        else:
            print("Error: Wakeword could not be processed")