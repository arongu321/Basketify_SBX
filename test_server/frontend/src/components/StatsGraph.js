import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Plot from "react-plotly.js";
import axios from "axios";
import logo from "../assets/Basketify-Logo.png";
import "./StatsGraph.css";

function StatsGraph() {
  const { type, name } = useParams();
  const navigate = useNavigate();
  const [statsData, setStatsData] = useState([]);
  const [seasonalStats, setSeasonalStats] = useState([]);
  const [currentSeasonStats, setCurrentSeasonStats] = useState([]);
  const [selectedStats, setSelectedStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSeasonal, setIsSeasonal] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/stats/${type}/${name}`
        );
        setStatsData(response.data.stats);
        setSeasonalStats(response.data.seasonal_stats);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching stats data:", error);
        setLoading(false);
      }
    };

    fetchStats();
  }, [type, name]);

  useEffect(() => {
    if (statsData.length > 0) {
      const currentSeason = statsData.filter((stat) => {
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

      setCurrentSeasonStats(currentSeason);
    }
  }, [statsData]);

  const handleStatChange = (event) => {
    const stat = event.target.value;
    setSelectedStats((prevStats) => {
      if (prevStats.includes(stat)) {
        return prevStats.filter((item) => item !== stat);
      } else {
        const newStats = [...prevStats, stat];
        return newStats.length > 2 ? newStats.slice(1) : newStats;
      }
    });
  };

  const handleToggleStats = () => {
    setIsSeasonal(!isSeasonal);
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <img src={logo} alt="Loading..." className="loading-favicon" />
        <h2>Loading...</h2>
      </div>
    );
  }

  const plotData = selectedStats.map((stat, index) => {
    const dataToUse = isSeasonal
      ? seasonalStats.slice().reverse()
      : currentSeasonStats;
    const xValues = dataToUse.map((data) =>
      isSeasonal ? data.season : new Date(data.date).toLocaleDateString()
    );
    const yValues = dataToUse.map((data) => data[stat] || 0);

    const formattedStatName = stat
      .replace(/([A-Z])/g, " $1")
      .replace(/^./, (str) => str.toUpperCase());

    return {
      type: "scatter",
      mode: "lines+markers",
      name: formattedStatName,
      x: xValues,
      y: yValues,
      yaxis: index === 1 ? "y2" : "y",
    };
  });

  const layout = {
    title: "Stats Over Time",
    xaxis: { title: isSeasonal ? "Season" : "Date" },
    yaxis: {
      title: {
        text: selectedStats[0]
          ? selectedStats[0]
              .replace(/([A-Z])/g, " $1")
              .replace(/^./, (str) => str.toUpperCase())
          : "",
        font: {
          size: 20,
          color: "#7f7f7f",
        },
      },
      side: "left",
      range:
        selectedStats.length > 0
          ? [
              0,
              Math.max(
                ...(isSeasonal
                  ? seasonalStats.slice().reverse()
                  : currentSeasonStats
                ).map((data) => data[selectedStats[0]] || 0)
              ) * 1.2,
            ]
          : undefined,
    },
    ...(selectedStats.length === 2 && {
      yaxis2: {
        title: {
          text: selectedStats[1]
            ? selectedStats[1]
                .replace(/([A-Z])/g, " $1")
                .replace(/^./, (str) => str.toUpperCase())
            : "",
          font: {
            size: 20,
            color: "#7f7f7f",
          },
        },
        side: "right",
        overlaying: "y",
        range: [
          0,
          Math.max(
            ...(isSeasonal
              ? seasonalStats.slice().reverse()
              : currentSeasonStats
            ).map((data) => data[selectedStats[1]] || 0)
          ) * 1.2,
        ],
      },
    }),
  };

  return (
    <div className="stats-graph-container">
      <div className="stats-graph-top-banner">
        <button
          className="stats-graph-back-button"
          onClick={() => navigate(-1)}
        >
          Back
        </button>
        <div className="header-content">
          <h1 className="title">
            Stats Graph: {type.charAt(0).toUpperCase() + type.slice(1)} - {name}
          </h1>
        </div>
      </div>

      <div className="stats-graph-selection-div">
        <h3>Select stats to plot (you can select up to 2 at a time):</h3>
        <div className="stats-graph-button-container">
          {[
            "points",
            "rebounds",
            "assists",
            "fieldGoalsMade",
            "threePointsMade",
            "fieldGoalPercentage",
            "threePointPercentage",
            "freeThrowsMade",
            "freeThrowPercentage",
            "steals",
            "blocks",
            "turnovers",
          ].map((stat) => (
            <button
              key={stat}
              value={stat}
              onClick={() => handleStatChange({ target: { value: stat } })}
              className={
                selectedStats.includes(stat)
                  ? "stats-graph-button active"
                  : "stats-graph-button"
              }
              disabled={
                selectedStats.length === 2 && !selectedStats.includes(stat)
              }
            >
              {stat
                .replace(/([A-Z])/g, " $1")
                .replace(/^./, (str) => str.toUpperCase())}
            </button>
          ))}
        </div>
        <button
          className="stats-graph-seasonal-stats-button"
          onClick={handleToggleStats}
        >
          {isSeasonal ? "Show Game-by-Game Stats" : "Show Seasonal Stats"}
        </button>
      </div>

      <div className="stats-graph-content">
        {selectedStats.length > 0 && (
          <div className="stats-graph-container-inner">
            <Plot
              data={plotData}
              layout={layout}
              className="stats-graph-plotly-graph"
            />
          </div>
        )}
      </div>

      <div className="bottom-banner"></div>
    </div>
  );
}

export default StatsGraph;
