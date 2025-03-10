# wakeword_detector.py
import speech_recognition as sr
import time

class WakewordDetector:
    def __init__(self, wakeword="hey lisa", listen_timeout=10, process_timeout=5): # Parameters here will be default but if the main changed it, it will be updated as main.py
        self.recognizer = sr.Recognizer()
        self.wakeword = wakeword.lower()
        self.listen_timeout = listen_timeout  # Timeout for initial listening
        self.process_timeout = process_timeout  # Timeout after hearing speech (also for the additional speech combined with the initial speech)
        
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
                    print(f"Speech detected! Processing for {self.process_timeout} seconds...")  # time that let the program to process the speech (it could be faster than that)
                    
                    # Phase 2: Process the speech and continue listening for a short time
                    start_time = time.time()
                    
                    text = self.recognizer.recognize_google(audio).lower() # Recognize the speech and convert it to lowercase text
                    print(f"Detected speech: {text}")
                    
                    # Check if wakeword is in the detected speech
                    if self.wakeword in text:
                        print("Wakeword detected!")
                        return 1  # Wakeword detected
                    

                    # If not, continue listening for the remaining time
                    remaining_time = self.process_timeout - (time.time() - start_time)
                    while remaining_time > 0:
                        print(f"Wakeword not found. Continuing to listen for {remaining_time:.1f} more seconds...")
                        remaining_time = self.process_timeout - (time.time() - start_time)
                        
                        try:
                            audio = self.recognizer.listen(source, timeout=remaining_time)
                            text = self.recognizer.recognize_google(audio).lower()
                            print(f"Additional speech detected: {text}")
                            
                            if self.wakeword in text:
                                print("Wakeword detected in follow-up!")
                                return 1  # Wakeword detected
                            else:
                                print("Wakeword not detected in follow-up. Retry again..")
                                # Speech detected but no wakeword
                        
                        except (sr.WaitTimeoutError):
                            print("No additional speech detected.")
                            return 0  # Speech detected but no wakeword
                        
                    # return -1  # Speech detected but no wakeword after processing timeout
                    
                    # except sr.UnknownValueError:  # For the initial speech
                    #     print("Could not understand initial audio")
                    #     return -1  # Speech detected but couldn't be understood
                
                except sr.WaitTimeoutError: # timout for first speech
                    print(f"No speech detected within {self.listen_timeout} seconds timeout")
                    return 0  # No speech detected
        
        except sr.RequestError as e:
            print(f"API Error: {e}")
            return -1
        
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