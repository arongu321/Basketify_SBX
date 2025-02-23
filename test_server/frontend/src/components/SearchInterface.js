import React, { useEffect, useState } from 'react';
import axios from 'axios';

function SearchInterface() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    // Fetch the search interface message from the Django server
    axios.get('http://localhost:8000/api/search-message/')
      .then(response => {
        setMessage(response.data.message);  // Set the message from the response
      })
      .catch(error => {
        console.error("There was an error fetching the search interface message:", error);
      });
  }, []);

  return (
    <div>
      <h1>Search Interface Page</h1>
      <p>{message}</p>
    </div>
  );
}

export default SearchInterface;
