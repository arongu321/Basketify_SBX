import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Login from './components/Login';
import SearchInterface from './components/SearchInterface';
import StatsPage from './components/StatsPage';
import StatsGraph from './components/StatsGraph';

function Home({ message }) {
  const [favorites, setFavorites] = useState({ player: null, team: null });
  const navigate = useNavigate();

  useEffect(() => {
    // fetch the user's favorite player and team from the backend
    axios.get('http://localhost:8000/api/user-favorites/')
      .then(response => {
        setFavorites({
          player: response.data.favorite_player,
          team: response.data.favorite_team
        });
      })
      .catch(error => {
        console.log('Error fetching favorites!', error);
      });
  }, []);

  const handleFavoriteClick = (type) => {
    if (type === 'player' && favorites.player) {
      navigate(`/stats/player/${favorites.player}`);
    } else if (type === 'team' && favorites.team) {
      navigate(`/stats/team/${favorites.team}`);
    } else {
      // pass a prop to indicate this is for setting a favorite
      navigate('/search', { state: { setFavorite: type } });
    }
  };

  return (
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
        <li>
          <button onClick={() => handleFavoriteClick('player')}>
            Favourite Player
          </button>
        </li>
        <li>
          <button onClick={() => handleFavoriteClick('team')}>
            Favourite Team
          </button>
        </li>
      </ul>
    </>
  );
}

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    axios.get('http://localhost:8000/api/load-database/');  // set up connection to DB ahead of time
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
          <Route path="/" element={<Home message={message} />} />
          <Route path="/login" element={<Login />} />
          <Route path="/search" element={<SearchInterface />} />
          <Route path="/stats/:type/:name" element={<StatsPage />} />
          <Route path="/stats-graph/:type/:name" element={<StatsGraph />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
