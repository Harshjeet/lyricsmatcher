import { useState } from "react";
import axios from "axios";
import "./App.css";  // Import the CSS file

function App() {
  const [lyrics, setLyrics] = useState("");
  const [guess, setGuess] = useState("");
  const [result, setResult] = useState(null);
  const [correctTitle, setCorrectTitle] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isChecking, setIsChecking] = useState(false);  // New state for checking loader

  const API_BASE = "http://localhost:5000/api";

  const generateLyrics = async () => {
    try {
      setIsLoading(true);
      setError("");
      setLyrics("");
      setResult(null);
      setCorrectTitle("");

      const response = await axios.post(`${API_BASE}/generate`, {}, { withCredentials: true });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      setTimeout(() => {
        setLyrics(response.data.lyrics);
        setIsLoading(false);
      }, 1500); 
    } catch (err) {
      console.error("Error generating lyrics:", err);
      setError(err.response?.data?.error || "Failed to get lyrics. Please try again.");
      setIsLoading(false);
    }
  };

  const checkAnswer = async () => {
    try {
      if (!guess.trim()) {
        setError("Please enter your guess");
        return;
      }

      setIsChecking(true);  
      const response = await axios.post(`${API_BASE}/check`, { guess: guess.trim() }, { withCredentials: true });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      setResult(response.data.is_correct);
      setCorrectTitle(response.data.correct_title);
      setError("");
    } catch (err) {
      console.error("Error checking answer:", err);
      setError("Failed to check answer. Please try again.");
    } finally {
      setIsChecking(false);  
    }
  };

  return (
    <div className="container">
      <h1 className="title">🎵 Lyric Match</h1>

      <div className="card">
        <button
          onClick={generateLyrics}
          disabled={isLoading}
          className="btn generate-btn"
        >
          {isLoading ? (
            <div className="loader"></div>
          ) : (
            "🎵 Generate Lyric Snippet"
          )}
        </button>

        {error && <div className="error">{error}</div>}

        {lyrics && (
          <div className="lyrics-box">
            <h2>🎤 Lyrics Snippet:</h2>
            <p>{lyrics}</p>
          </div>
        )}

        {lyrics && (
          <div className="input-group">
            <input
              type="text"
              value={guess}
              onChange={(e) => setGuess(e.target.value)}
              placeholder="Enter your guess..."
              className="input"
            />
            <button
              onClick={checkAnswer}
              className="btn check-btn"
              disabled={isChecking}
            >
              {isChecking ? "🔍 Checking..." : "✅ Check Answer"}
            </button>
          </div>
        )}

        {result !== null && (
          <div className={`result ${result ? "correct" : "incorrect"}`}>
            {result ? (
              <div>
                🎉 Correct Answer!
                <p>✅ You guessed it right!</p>
              </div>
            ) : (
              <div>
                ❌ Incorrect Guess!
                <p>Correct song was: <strong>{correctTitle}</strong></p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
