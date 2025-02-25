import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import Login from './components/Login';
import SearchInterface from './components/SearchInterface';
import StatsPage from './components/StatsPage'; // Import StatsPage

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    axios.get('http://localhost:8000/api/')
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        console.log('There was an error!', error);
      });
  }, []);

  return (
    <Router>
      <div>
        <Routes>
          {/* Home route with navigation */}
          <Route
            path="/"
            element={
              <>
                <h1>Message from Django server: {message}</h1>
                <p>Click on the links below to go to other pages:</p>
                <ul>
                  <li>
                    <Link to="/login">Go to Login</Link>
                  </li>
                  <li>
                    <Link to="/search">Go to Search Interface</Link>
                  </li>
                </ul>
              </>
            }
          />
          
          {/* Login route */}
          <Route path="/login" element={<Login />} />
          
          {/* Search Interface route */}
          <Route path="/search" element={<SearchInterface />} />
          
          {/* Stats route - players ans teams */}
          <Route path="/stats/:type/:name" element={<StatsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
