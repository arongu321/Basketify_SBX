import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import logo from "../assets/Basketify-Logo.png";
import "./StatsPage.css";

function StatsPage() {
  const { type, name } = useParams();
  const navigate = useNavigate();
  const [statsData, setStatsData] = useState([]);
  const [seasonalStats, setSeasonalStats] = useState([]);
  const [currentSeasonStats, setCurrentSeasonStats] = useState([]);
  const [futureGames, setFutureGames] = useState([]);
  const [isSeasonal, setIsSeasonal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/stats/${type}/${name}`
        );

        const { stats, seasonal_stats } = response.data;

        const currentSeason = stats.filter((stat) => {
          const statDate = new Date(stat.date);
          const currentDate = new Date();
          let seasonStart = new Date(currentDate.getFullYear(), 9, 1);
          let seasonEnd = new Date(currentDate.getFullYear() + 1, 8, 31);

          if (currentDate.getMonth() < 9) {
            seasonStart = new Date(currentDate.getFullYear() - 1, 9, 1);
            seasonEnd = new Date(currentDate.getFullYear(), 8, 31);
          }

          return statDate >= seasonStart && statDate <= seasonEnd && !stat.is_future_game;
        });

        const futureGames = stats.filter((stat) => stat.is_future_game);

        setStatsData(stats);
        setSeasonalStats(seasonal_stats);
        setCurrentSeasonStats(currentSeason);
        setFutureGames(futureGames);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching stats data:", error);
        setLoading(false);
      }
    };

    fetchStats();
  }, [type, name]);

  const handleToggleStats = () => {
    setIsSeasonal(!isSeasonal);
  };

  const handleGoToGraph = () => {
    navigate(`/stats-graph/${type}/${name}`);
  };

  if (loading) {
    return (
      <div className="stats-page-loading-screen">
        <img
          src={logo}
          alt="Loading..."
          className="stats-page-loading-favicon"
        />
        <h2>Loading...</h2>
      </div>
    );
  }

  return (
    <div className="stats-page-container">
      <div className="stats-page-top-banner">
        <button className="stats-page-back-button" onClick={() => navigate(-1)}>
          Back
        </button>
        <div className="stats-page-header-content">
          <h1 className="stats-page-title">
            {type.charAt(0).toUpperCase() + type.slice(1)} Stats: {name}
          </h1>
        </div>
      </div>

      <div className="stats-page-content">
        <div className="stats-page-button-container">
          <button onClick={handleToggleStats}>
            {isSeasonal ? "Show Game-by-Game Stats" : "Show Seasonal Stats"}
          </button>
          <button onClick={handleGoToGraph}>View Stats Graph</button>
        </div>

        {statsData.length === 0 ? (
          <p>No stats available for this {type}.</p>
        ) : (
          <div>
            <table className="stats-page-table">
              <thead>
                <tr>
                  <th>{isSeasonal ? "Season" : "Date"}</th>
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
                {(isSeasonal ? seasonalStats : currentSeasonStats)
                  .slice()
                  .reverse()
                  .map((gameStats, index) => (
                    <tr key={index}>
                      <td>
                        {isSeasonal
                          ? gameStats.season
                          : new Date(gameStats.date).toLocaleDateString()}
                      </td>
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

            <h2>Future Games</h2>
            <table className="stats-page-table">
              <thead>
                <tr>
                  <th>Date</th>
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
                {futureGames.map((gameStats, index) => (
                  <tr key={index}>
                    <td>{new Date(gameStats.date).toLocaleDateString()}</td>
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
          </div>
        )}
      </div>

      <div className="stats-page-bottom-banner"></div>
    </div>
  );
}

export default StatsPage;
