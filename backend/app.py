from flask import Flask, request, jsonify, session
from flask_cors import CORS
import random
from transformers import pipeline
from songs import SONG_TITLES
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'sdkjfsU&$jb&&hEee8'  
# Add these configurations after initializing the Flask app
app.config.update(
    SESSION_COOKIE_SECURE=False,  
    SESSION_COOKIE_SAMESITE='Lax' 
)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# Load the FLAN-T5 model
logger.info("Loading FLAN-T5 model...")
lyric_generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    device=-1  
)
logger.info("Model loaded successfully")

def generate_lyrics_prompt(song_title):
    return f"""Generate 3-4 lines of lyrics from the song "{song_title}" without mentioning the title.
The lyrics should be recognizable but not directly reveal the song title. Put each line on a new line.

Example:
Input: "Hotel California - Eagles"
Output:
On a dark desert highway, cool wind in my hair
Warm smell of colitas rising up through the air
Up ahead in the distance, I saw a shimmering light

Now generate for "{song_title}":
"""

def clean_lyrics(text):
    # Remove unwanted phrases and normalize
    removals = ["Output:", "Lyrics:", "Song:", "**", "*"]
    for phrase in removals:
        text = text.replace(phrase, "")
    
    # Process lines and preserve newlines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

@app.route('/api/generate', methods=['POST'])
def generate_snippet():
    try:
        selected_song = random.choice(SONG_TITLES)
        logger.info(f"Generating lyrics for: {selected_song}")
        
        # Generate lyrics
        response = lyric_generator(
            generate_lyrics_prompt(selected_song),
            max_length=1000, 
            num_return_sequences=1,
            temperature=0.9,
            do_sample=True
        )
        
        lyrics = clean_lyrics(response[0]['generated_text'])
        
        # Store correct answer in session
        session['correct_title'] = selected_song
        
        return jsonify({
            'lyrics': lyrics,
            'error': None
        })
    
    except Exception as e:
        logger.error(f"Error generating lyrics: {str(e)}")
        return jsonify({
            'lyrics': None,
            'error': "Failed to generate lyrics. Please try again."
        }), 500

@app.route('/api/check', methods=['POST'])
def check_answer():
    try:
        data = request.get_json()
        user_guess = data.get('guess', '').strip().lower()
        correct_title = session.get('correct_title', '').lower()
        
        if not user_guess:
            return jsonify({'error': 'No guess provided'}), 400
        
        # Simple fuzzy matching
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