import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';

function StatsPage() {
  const { type, name } = useParams(); // Get 'type' and 'name' from the URL using useParams
  const navigate = useNavigate(); // To navigate to StatsGraph page
  const [statsData, setStatsData] = useState([]);
  const [seasonalStats, setSeasonalStats] = useState([]);
  const [currentSeasonStats, setCurrentSeasonStats] = useState([]);
  const [isSeasonal, setIsSeasonal] = useState(false); // Track if the user wants seasonal stats or game-by-game
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch stats data for the player/team
    const fetchStats = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/stats/${type}/${name}`);
        const stats = response.data.stats;

        // Filter stats for the current season
        const currentSeason = stats.filter(stat => stat.year === new Date().getFullYear());

        setStatsData(stats);
        setCurrentSeasonStats(currentSeason);
        setSeasonalStats(stats); // Set all stats for later use
        setLoading(false);
      } catch (error) {
        console.error("There was an error fetching the stats data:", error);
        setLoading(false);
      }
    };

    fetchStats();
  }, [type, name]); // Re-run the effect when the type or name changes

  if (loading) {
    return <div>Loading...</div>;
  }

  // Toggle between seasonal stats and current season stats
  const handleToggleStats = () => {
    setIsSeasonal(!isSeasonal);
  };

  // Handle navigation to graph view
  const handleGoToGraph = () => {
    navigate(`/stats-graph/${type}/${name}`);
  };

  return (
    <div>
      <h1>{type.charAt(0).toUpperCase() + type.slice(1)} Stats: {name}</h1>
      
      <div className="button-container">
        <button onClick={handleToggleStats}>
          {isSeasonal ? 'Show Game-by-Game Stats' : 'Show Seasonal Stats'}
        </button>
        <button onClick={handleGoToGraph}>View Stats Graph</button>
      </div>

      {statsData.length === 0 ? (
        <p>No stats available for this {type}.</p>
      ) : (
        <table border="1">
          <thead>
            <tr>
              <th>Year</th>
              <th>Points Scored</th>
              <th>Rebounds</th>
              <th>Assists</th>
              <th>Field Goals Made</th>
              <th>Field Goal %</th>
              <th>3P Made</th>
              <th>3P %</th>
              <th>Free Throws Made</th>
              <th>Free Throw %</th>
              <th>Steals</th>
              <th>Blocks</th>
              <th>Turnovers</th>
            </tr>
          </thead>
          <tbody>
            {(isSeasonal ? seasonalStats : currentSeasonStats).map((yearStats, index) => (
              <tr key={index}>
                <td>{yearStats.year}</td>
                <td>{yearStats.points}</td>
                <td>{yearStats.rebounds}</td>
                <td>{yearStats.assists}</td>
                <td>{yearStats.fieldGoalsMade}</td>
                <td>{yearStats.fieldGoalPercentage}%</td>
                <td>{yearStats.threePointsMade}</td>
                <td>{yearStats.threePointPercentage}%</td>
                <td>{yearStats.freeThrowsMade}</td>
                <td>{yearStats.freeThrowPercentage}%</td>
                <td>{yearStats.steals}</td>
                <td>{yearStats.blocks}</td>
                <td>{yearStats.turnovers}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default StatsPage;
