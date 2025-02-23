import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Login() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    // Fetch the login message from the Django server
    axios.get('http://localhost:8000/api/login-message/')
      .then(response => {
        setMessage(response.data.message);  // Set the message from the response
      })
      .catch(error => {
        console.error("There was an error fetching the login message:", error);
      });
  }, []);

  return (
    <div>
      <h1>Login Page</h1>
      <p>{message}</p>
    </div>
  );
}

export default Login;
