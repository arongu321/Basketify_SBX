import React, { useEffect, useState } from 'react';
import axios from 'axios';

function MLPredictions() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    // Fetch the predictions message from the Django server
    axios.get('http://localhost:8000/api/predictions-message/')
      .then(response => {
        setMessage(response.data.message);  // Set the message from the response
      })
      .catch(error => {
        console.error("There was an error fetching the predictions message:", error);
      });
  }, []);

  return (
    <div>
      <h1>ML Predictions Page</h1>
      <p>{message}</p>
    </div>
  );
}

export default MLPredictions;
