import os
import re
import sounddevice as sd
import soundfile as sf
# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Define the pronunciation rules
number_pronunciations = {
    1: "1.wav",
    2: "2.wav",
    3: "3.wav",
    4: "4.wav",
    5: "5.wav",
    6: "6.wav",
    7: "7.wav",
    8: "8.wav",
    9: "9.wav",
    10: "10.wav",
    20: "20-90.wav+2.wav",
    30: "20-90.wav+3.wav",
    40: "20-90.wav+4.wav",
    50: "20-90.wav+5.wav",
    60: "20-90.wav+6.wav",
    70: "20-90.wav+7.wav",
    80: "20-90.wav+8.wav",
    90: "20-90.wav+9.wav",
    100: "100.wav",
    1000: "1000.wav",
    1000000: "1000000.wav"
}

# Function to pronounce a number
def pronounce_number(number):
    if number in number_pronunciations:
        pronunciation = number_pronunciations[number]
    else:
        if number < 20:
            pronunciation = f"10.wav+KƐ.wav+{number % 10}.wav"
        elif number < 100:
            tens = (number // 10) * 10
            units = number % 10
            pronunciation = f"20-90.wav+{tens // 10}.wav+KƐ.wav+{units}.wav" if units != 0 else f"20-90.wav+{tens // 10}.wav"
        elif number < 1000:
            hundreds = number // 100
            remainder = number % 100
            pronunciation = f"100.wav+{hundreds}.wav+KƐ.wav+{pronounce_number(remainder)}" if remainder != 0 else f"100.wav+{hundreds}.wav"
        elif number < 1000000:
            thousands = number // 1000
            remainder = number % 1000
            pronunciation = f"1000.wav+{pronounce_number(thousands)}+KƐ.wav+{pronounce_number(remainder)}" if remainder != 0 else f"1000.wav+{pronounce_number(thousands)}"
        else:
            millions = number // 1000000
            remainder = number % 1000000
            pronunciation = f"1000000.wav+{pronounce_number(millions)}+KƐ.wav+{pronounce_number(remainder)}" if remainder != 0 else f"1000000.wav+{pronounce_number(millions)}"
    
    # Split the pronunciation into individual .wav files
    wav_files = pronunciation.split('+')
    
    # Pronounce each .wav file
    for wav in wav_files:
        engine.say(wav)
    
    engine.runAndWait()

# Example usage
pronounce_number(123)
pronounce_number(2000)
pronounce_number(3468567)