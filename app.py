from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
import random
import requests
from songs import SONG_TITLES
import logging
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'sdkjfsU&$jb&&hEee8'
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE='Lax'
)
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "https://lyricsmatcher.onrender.com"])



# Hugging Face API configuration
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
API_TOKEN = "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" 
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  #

def generate_lyrics_prompt(song_title):
    """Generate a prompt that clearly separates instructions from the expected output."""
    title, artist = song_title.split(' - ')
    return f"""Write 4 lines of song lyrics in the style and mood of "{title}" by {artist}.
The lyrics should reflect the song's themes and rhythm without mentioning the title or artist.
Use metaphors and poetic language consistent with the song's style.

Lyrics:
"""

def clean_lyrics(text):
    """Clean and format the lyrics, removing the initial prompt part."""
    if not text:
        return "No lyrics generated."

    # Split the text to remove any part before and including "Lyrics:"
    parts = re.split(r'Lyrics:\s*', text, flags=re.IGNORECASE)
    lyrics_part = parts[-1] 

    # Remove unwanted patterns and markdown
    unwanted_patterns = [
        r"Output:", 
        r"Song:", 
        r"\*\*.*?\*\*", 
        r"\*.*?\*"       
    ]

    for pattern in unwanted_patterns:
        lyrics_part = re.sub(pattern, '', lyrics_part, flags=re.IGNORECASE)

    # Extract lines and ensure only 4 are kept
    lines = [line.strip() for line in lyrics_part.split('\n') if line.strip()]
    return '\n'.join(lines[:4]) if lines else "No valid lyrics generated."
def query_huggingface_api(payload):
    """Query the Hugging Face API with retry logic."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Attempt {attempt} to query Hugging Face API...")

            response = requests.post(
                API_URL, headers=headers, json=payload, timeout=15
            )

            if response.status_code == 200:
                return response.json()

            logger.warning(f"Failed attempt {attempt}: {response.status_code} - {response.text}")

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
            else:
                response.raise_for_status()

        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
            else:
                raise

    raise Exception("Failed to query Hugging Face API after retries.")

@app.route('/api/generate', methods=['POST'])
def generate_snippet():
    try:
        selected_song = random.choice(SONG_TITLES)
        logger.info(f"Generating lyrics for: {selected_song}")

        prompt = generate_lyrics_prompt(selected_song)
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 150,
                "temperature": 0.85,
                "do_sample": True
            }
        }

        response = query_huggingface_api(payload)

        if isinstance(response, list) and len(response) > 0 and 'generated_text' in response[0]:
            lyrics = clean_lyrics(response[0]['generated_text'])
        else:
            lyrics = "No lyrics generated. Please try again."

        session['correct_title'] = selected_song

        res = make_response(jsonify({'lyrics': lyrics, 'error': None}))
        res.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:5173')
        res.headers['Access-Control-Allow-Credentials'] = 'true'
        return res

    except Exception as e:
        logger.error(f"Error generating lyrics: {str(e)}")
        res = make_response(jsonify({'lyrics': None, 'error': "Failed to generate lyrics. Please try again later."}))
        res.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:5173')
        res.headers['Access-Control-Allow-Credentials'] = 'true'
        return res, 500


@app.route('/api/check', methods=['POST'])
def check_answer():
    """Check user's guess against the correct song title."""
    try:
        data = request.get_json()
        user_guess = data.get('guess', '').strip().lower()
        correct_title = session.get('correct_title', '').lower()

        if not user_guess:
            return jsonify({'error': 'No guess provided'}), 400

        is_correct = any([
            user_guess in correct_title,
            correct_title.split('-')[0].strip().lower() in user_guess
        ])

        return jsonify({
            'is_correct': is_correct,
            'correct_title': session.get('correct_title', 'Unknown Song')
        })

    except Exception as e:
        logger.error(f"Error checking answer: {str(e)}")
        return jsonify({'error': 'Failed to check answer'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)