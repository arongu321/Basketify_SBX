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

        const stats = response.data.stats;


        // get current season (e.g. "2024-2025")
        const getSeason = (date) => {
          const month = new Date(date).getMonth() + 1;  // indexed at 1
          const year = new Date(date).getFullYear();
          
          if (month >= 10) {
            return `${year}-${year + 1}`; // Oct to Dec, season started this year
          } else {
            return `${year - 1}-${year}`; // Jan to Sep, season started last year
          }
        };

        // group stats by season, doing this aggregation on frontend
        const groupedBySeason = stats.reduce((acc, stat) => {
          const season = getSeason(stat.date);
          
          if (!acc[season]) {
            acc[season] = {
              season: season,  // season is key
              points: 0,
              rebounds: 0,
              assists: 0,
              fieldGoalsMade: 0,
              fieldGoalsAttempted: 0,
              fieldGoalPercentage: 0,
              threePointsMade: 0,
              threePointsAttempted: 0,
              threePointPercentage: 0,
              freeThrowsMade: 0,
              freeThrowsAttempted: 0,
              freeThrowPercentage: 0,
              steals: 0,
              blocks: 0,
              turnovers: 0,
              gamesPlayed: 0
            };
          }
          
          acc[season].points += stat.points || 0;
          acc[season].rebounds += stat.rebounds || 0;
          acc[season].assists += stat.assists || 0;
          acc[season].fieldGoalsMade += stat.fieldGoalsMade || 0;
          acc[season].fieldGoalsAttempted += stat.fieldGoalsMade / stat.fieldGoalPercentage || 0;
          acc[season].fieldGoalPercentage = acc[season].fieldGoalsMade / acc[season].fieldGoalsAttempted || 0;
          acc[season].threePointsMade += stat.threePointsMade || 0;
          acc[season].threePointsAttempted += stat.threePointsMade / stat.threePointPercentage || 0;
          acc[season].threePointPercentage = acc[season].threePointsMade / acc[season].threePointsAttempted || 0;
          acc[season].freeThrowsMade += stat.freeThrowsMade || 0;
          acc[season].freeThrowsAttempted += stat.freeThrowsMade / stat.freeThrowPercentage || 0;
          acc[season].freeThrowPercentage = acc[season].freeThrowsMade / acc[season].freeThrowsAttempted || 0;
          acc[season].steals += stat.steals || 0;
          acc[season].blocks += stat.blocks || 0;
          acc[season].turnovers += stat.turnovers || 0;
          acc[season].gamesPlayed += 1;

          return acc;
        }, {});

        // convert object to array
        const seasonalStatsArray = Object.values(groupedBySeason);

        // get current season stats (what's displayed by default)
        const currentSeason = stats.filter(stat => {
          const statDate = new Date(stat.date);
          const currentDate = new Date();
          
          // curr season start & end date
          let seasonStart = new Date(currentDate.getFullYear(), 9, 1); // sept 1 of curr year
          let seasonEnd = new Date(currentDate.getFullYear() + 1, 8, 31); // aug 31 of next year

          // adjust season if current date is before September
          if (currentDate.getMonth() < 9) {
            seasonStart = new Date(currentDate.getFullYear() - 1, 9, 1); // sept 1st of previous year
            seasonEnd = new Date(currentDate.getFullYear(), 8, 31); // aug 31 of curr year
          }

          return statDate >= seasonStart && statDate <= seasonEnd;
        });

        setStatsData(stats);
        setSeasonalStats(seasonalStatsArray);
        setCurrentSeasonStats(currentSeason);
        setLoading(false);
      } catch (error) {
        console.error("There was an error fetching the stats data:", error);
        setLoading(false);
      }
    };

    fetchStats();
  }, [type, name]); // re-run the effect when type or name changes  

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
            {(isSeasonal ? seasonalStats : currentSeasonStats).map((gameStats, index) => (
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
