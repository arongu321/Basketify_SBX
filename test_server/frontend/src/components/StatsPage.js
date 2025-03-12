import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';

function StatsPage() {
  const { type, name } = useParams(); // get 'type' (player or team) and 'name' from the URL using useParams
  const navigate = useNavigate(); // navigate to statsGraph
  const [statsData, setStatsData] = useState([]);
  const [seasonalStats, setSeasonalStats] = useState([]);
  const [currentSeasonStats, setCurrentSeasonStats] = useState([]);
  const [isSeasonal, setIsSeasonal] = useState(false); // track if user wants seasonal stats or game-by-game
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/stats/${type}/${name}`);

        const { stats, seasonal_stats } = response.data;

        // get current season stats
        const currentSeason = stats.filter(stat => {
          const statDate = new Date(stat.date);
          const currentDate = new Date();
          
          let seasonStart = new Date(currentDate.getFullYear(), 9, 1);
          let seasonEnd = new Date(currentDate.getFullYear() + 1, 8, 31);

          if (currentDate.getMonth() < 9) {
            seasonStart = new Date(currentDate.getFullYear() - 1, 9, 1);
            seasonEnd = new Date(currentDate.getFullYear(), 8, 31);
          }

          return statDate >= seasonStart && statDate <= seasonEnd;
        });

        setStatsData(stats);
        setSeasonalStats(seasonal_stats);
        setCurrentSeasonStats(currentSeason);
        setLoading(false);
      } catch (error) {
        console.error("There was an error fetching the stats data:", error);
        setLoading(false);
      }
    };

    fetchStats();
  }, [type, name]); 

  if (loading) {
    return <div>Loading...</div>;
  }

  // toggle between seasonal stats and current season stats
  const handleToggleStats = () => {
    setIsSeasonal(!isSeasonal);
  };

  // handle navigation to graph view
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
              <th>{isSeasonal ? 'Season' : 'Date'}</th>
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
            {(isSeasonal ? seasonalStats.slice().reverse() : currentSeasonStats.slice().reverse()).map((gameStats, index) => (
              <tr key={index}>
                <td>{isSeasonal ? gameStats.season : new Date(gameStats.date).toLocaleDateString()}</td>
                <td>{gameStats.points}</td>
                <td>{gameStats.rebounds}</td>
                <td>{gameStats.assists}</td>
                <td>{gameStats.fieldGoalsMade}</td>
                <td>{(gameStats.fieldGoalPercentage * 100).toFixed(1)}%</td>
                <td>{gameStats.threePointsMade}</td>
                <td>{(gameStats.threePointPercentage * 100).toFixed(1)}%</td>
                <td>{gameStats.freeThrowsMade}</td>
                <td>{(gameStats.freeThrowPercentage * 100).toFixed(1)}%</td>
                <td>{gameStats.steals}</td>
                <td>{gameStats.blocks}</td>
                <td>{gameStats.turnovers}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default StatsPage;
