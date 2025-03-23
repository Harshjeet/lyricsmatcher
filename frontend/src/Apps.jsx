import { useState } from "react";
import axios from "axios";

function App() {
  const [lyrics, setLyrics] = useState("");
  const [guess, setGuess] = useState("");
  const [result, setResult] = useState(null);
  const [correctTitle, setCorrectTitle] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const API_BASE = "http://localhost:5000/api";

  const generateLyrics = async () => {
    try {
      setIsLoading(true);
      setError("");
      setLyrics(""); // Clear old lyrics when generating new ones
      setResult(null);
      setCorrectTitle("");
      
      const response = await axios.post(`${API_BASE}/generate`, {}, { withCredentials: true });

      setTimeout(() => {
        setLyrics(response.data.lyrics);
        setIsLoading(false);
      }, 1500); // Artificial delay for smoother transition
    } catch (err) {
      setError("Failed to generate lyrics. Please try again.");
      setIsLoading(false);
    }
  };

  const checkAnswer = async () => {
    try {
      if (!guess.trim()) {
        setError("Please enter your guess");
        return;
      }

      const response = await axios.post(`${API_BASE}/check`, { guess: guess.trim() }, { withCredentials: true });

      setResult(response.data.is_correct);
      setCorrectTitle(response.data.correct_title);
      setError("");
    } catch (err) {
      setError("Failed to check answer. Please try again.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-700 to-purple-900 px-4 text-white">
      {/* App Title */}
      <h1 className="text-5xl font-extrabold mb-8 text-center drop-shadow-lg">🎵 Lyric Match</h1>

      {/* Main Container */}
      <div className="w-full max-w-xl bg-white/10 backdrop-blur-lg shadow-2xl rounded-3xl p-8 space-y-6 text-center border border-white/20">

        {/* Generate Button with Spinner */}
        <button
          onClick={generateLyrics}
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 py-4 bg-blue-600 text-white text-lg font-semibold rounded-xl shadow-lg hover:bg-blue-700 transition-all duration-300 disabled:bg-gray-500 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <div className="h-6 w-6 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : (
            "Generate Lyric Snippet"
          )}
        </button>

        {/* Error Message */}
        {error && (
          <div className="text-red-600 bg-red-200 p-3 rounded-md shadow-md">{error}</div>
        )}

        {/* Lyrics Display (Hidden until generated) */}
        {lyrics && (
          <div className="bg-gray-100 p-4 rounded-lg shadow-md">
            <h2 className="text-lg font-semibold text-gray-800">Lyrics Snippet:</h2>
            <p className="text-gray-600 italic mt-2">{lyrics}</p>
          </div>
        )}

        {/* Guess Input (Only shown after lyrics are generated) */}
        {lyrics && (
          <div className="space-y-4">
            <input
              type="text"
              value={guess}
              onChange={(e) => setGuess(e.target.value)}
              placeholder="Enter your guess..."
              className="w-full border border-gray-300 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm text-gray-700"
            />

            {/* Check Answer Button */}
            <button
              onClick={checkAnswer}
              className="w-full py-3 bg-green-600 text-white text-lg font-semibold rounded-xl shadow-lg hover:bg-green-700 transition-all duration-300"
            >
              Check Answer
            </button>
          </div>
        )}

        {/* Result Display */}
        {result !== null && (
          <div
            className={`p-4 rounded-xl shadow-md ${
              result ? "bg-green-200 text-green-700" : "bg-red-200 text-red-700"
            }`}
          >
            {result ? "🎉 Correct Answer!" : "❌ Incorrect Guess!"}
            {!result && (
              <p className="mt-2 text-gray-600">
                Correct song was:{" "}
                <span className="font-semibold text-gray-800">{correctTitle}</span>
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
