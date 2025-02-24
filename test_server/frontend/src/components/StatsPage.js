import React, { useEffect, useState } from 'react';
import axios from 'axios';

function StatsPage({ match }) {
  const { type, name } = match.params; // Extract 'type' (player/team) and 'name' from the URL
  const [statsData, setStatsData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch stats data for the player/team
    const fetchStats = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/stats/${type}/${name}`);
        setStatsData(response.data.stats); // Assume 'stats' is the key in the response
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

  return (
    <div>
      <h1>{type.charAt(0).toUpperCase() + type.slice(1)} Stats: {name}</h1>
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
            {statsData.map((yearStats, index) => (
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
