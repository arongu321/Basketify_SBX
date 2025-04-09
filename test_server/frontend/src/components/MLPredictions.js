import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/Basketify-Logo.png';
import '../styles/MLPredictions.css';

function MLPredictions() {
  const [topTeam, setTopTeam] = useState('');
  const [topTeamPpg, setTopTeamPpg] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get('http://localhost:8000/api/predict-season-champion/')
      .then((response) => {
        setTopTeam(response.data.top_team);
        setTopTeamPpg(response.data.top_team_ppg);
        setLoading(false);
      })
      .catch((error) => {
        console.error("There was an error fetching the predicted NBA champion:", error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="ml-predictions-loading-screen">
        <img src={logo} alt="Loading..." className="ml-predictions-loading-favicon" />
        <h2>Loading Predictions...</h2>
      </div>
    );
  }

  return (
    <div className="ml-predictions-container">
      {/* Top Banner with Back Button */}
      <div className="ml-predictions-top-banner">
        <button className="ml-predictions-back-button" onClick={() => navigate(-1)}>Back</button>
        <div className="ml-predictions-header-content">
          <h1 className="ml-predictions-title">ML Predictions</h1>
        </div>
      </div>

      {/* Fulfills FR22 by displaying predicted NBA champion */}
      <div className="ml-predictions-content">
        <div className="ml-predictions-card">
          <h2>Predicted NBA Champion: {topTeam}</h2>
          <p>Average predicted points per game: {topTeamPpg}</p>
        </div>
      </div>

      {/* Bottom Banner */}
      <div className="ml-predictions-bottom-banner"></div>
    </div>
  );
}

export default MLPredictions;
