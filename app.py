from flask import Flask, request, jsonify
import pyttsx3  # TTS library

app = Flask(__name__)

@app.route('/tts', methods=['POST'])
def tts():
    text = request.json.get('text')  # Getting the text from the request body
    if text:
        engine = pyttsx3.init()  # Initialize the TTS engine
        audio_file = 'output.mp3'  # The output audio file
        engine.save_to_file(text, audio_file)  # Save audio to file
        engine.runAndWait()
        return jsonify({"message": "Audio generated", "audio_file": audio_file}), 200
    return jsonify({"error": "No text provided"}), 400

if __name__ == '__main__':
    app.run(debug=True)
