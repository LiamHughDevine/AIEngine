import React, { useState } from "react";
import "./App.css";

function StartButton() {
  // State to store the response from the server
  const [responseMessage, setResponseMessage] = useState("");

  const startButtonPressed = async () => {
    try {
      const context = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: "Please open word",
        }),
      });

      // Get the JSON response from the server
      const data = await context.json();

      // Set the response message to the state
      setResponseMessage(JSON.stringify(data, null, 2)); // Display formatted JSON
    } catch (error) {
      console.error("Error:", error);
      setResponseMessage("Failed to fetch response.");
    }
  };

  return (
    <div className="container">
      <button
        type="button"
        className="btn btn-dark"
        onClick={startButtonPressed}
      >
        Start
      </button>

      {/* Textbox to display the response */}
      <textarea
        value={responseMessage}
        onChange={(e) => setResponseMessage(e.target.value)} // Allow editing if desired
        rows="10"
        cols="50"
        placeholder="Response will appear here..."
      />
    </div>
  );
}

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <StartButton />
      </header>
    </div>
  );
}

export default App;
