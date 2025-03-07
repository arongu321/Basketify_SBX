import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'; 
import Plot from 'react-plotly.js';
import axios from 'axios';

function StatsGraph() {
  const { type, name } = useParams();
  const [statsData, setStatsData] = useState([]);
  const [seasonalStats, setSeasonalStats] = useState([]); 
  const [currentSeasonStats, setCurrentSeasonStats] = useState([]); 
  const [selectedStats, setSelectedStats] = useState([]); 
  const [loading, setLoading] = useState(true);
  const [isSeasonal, setIsSeasonal] = useState(false); 

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/stats/${type}/${name}`);
        setStatsData(response.data.stats);
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
      const groupedBySeason = statsData.reduce((acc, stat) => {
        const season = getSeason(stat.date);
        
        if (!acc[season]) {
          acc[season] = {
            season: season,  
            points: 0,
            rebounds: 0,
            assists: 0,
            fieldGoalsMade: 0,
            fieldGoalPercentage: 0,
            threePointsMade: 0,
            threePointPercentage: 0,
            freeThrowsMade: 0,
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
        acc[season].fieldGoalPercentage += stat.fieldGoalPercentage || 0;
        acc[season].threePointsMade += stat.threePointsMade || 0;
        acc[season].threePointPercentage += stat.threePointPercentage || 0;
        acc[season].freeThrowsMade += stat.freeThrowsMade || 0;
        acc[season].freeThrowPercentage += stat.freeThrowPercentage || 0;
        acc[season].steals += stat.steals || 0;
        acc[season].blocks += stat.blocks || 0;
        acc[season].turnovers += stat.turnovers || 0;
        acc[season].gamesPlayed += 1;

        return acc;
      }, {});

      const seasonalStatsArray = Object.values(groupedBySeason);

      const currentSeason = statsData.filter(stat => {
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

      setSeasonalStats(seasonalStatsArray);
      setCurrentSeasonStats(currentSeason);
    }
  }, [statsData]);

  const getSeason = (date) => {
    const month = new Date(date).getMonth() + 1;
    const year = new Date(date).getFullYear();
    
    if (month >= 10) {
      return `${year}-${year + 1}`;
    } else {
      return `${year - 1}-${year}`;
    }
  };

  const handleStatChange = (event) => {
    const stat = event.target.value;
    setSelectedStats(prevStats => {
      if (prevStats.includes(stat)) {
        return prevStats.filter(item => item !== stat);
      } else {
        return [...prevStats, stat];
      }
    });
  };

  const handleToggleStats = () => {
    setIsSeasonal(!isSeasonal);
  };

  if (loading) return <div>Loading...</div>;

  const plotData = selectedStats.map((stat, index) => {
    const xValues = isSeasonal 
      ? seasonalStats.map((data) => data.season) 
      : currentSeasonStats.map((data) => new Date(data.date).toLocaleDateString()); 

    const yValues = isSeasonal 
      ? seasonalStats.map((data) => data[stat.toLowerCase().replace(' ', '')]) 
      : currentSeasonStats.map((data) => data[stat.toLowerCase().replace(' ', '')]); 

    const yaxis = index === 0 ? { title: stat, side: 'left' } : { title: stat, side: 'right' };

    return {
      type: 'scatter',
      mode: 'lines+markers',
      name: stat,
      x: xValues,
      y: yValues,
      yaxis: `y${index + 1}`,
    };
  });

  // 2 y axes if 2 stats are selected
  const layout = {
    title: 'Stats Over Time',
    xaxis: { title: isSeasonal ? 'Season' : 'Date' }, 
    yaxis: { title: selectedStats[0], side: 'left' }, 
    yaxis2: selectedStats.length > 1
      ? {
          title: selectedStats[1],
          side: 'right',
          overlaying: 'y',
          range: [
            0,
            Math.max(
              ...statsData.map((data) => data[selectedStats[1].toLowerCase().replace(' ', '')])
            ),
          ], 
        }
      : null,
  };

  return (
    <div>
      <h1>Stats Graph: {type.charAt(0).toUpperCase() + type.slice(1)} - {name}</h1>

      <div>
        <h3>Select stats to plot:</h3>
        <label>
          <input
            type="checkbox"
            value="points"
            onChange={handleStatChange}
            disabled={selectedStats.length === 2 && !selectedStats.includes("points")}
          />
          Points Scored
        </label>
        <label>
          <input
            type="checkbox"
            value="rebounds"
            onChange={handleStatChange}
            disabled={selectedStats.length === 2 && !selectedStats.includes("rebounds")}
          />
          Rebounds
        </label>
        <label>
          <input
            type="checkbox"
            value="assists"
            onChange={handleStatChange}
            disabled={selectedStats.length === 2 && !selectedStats.includes("assists")}
          />
          Assists
        </label>
        <label>
          <input
            type="checkbox"
            value="fieldGoalsMade"
            onChange={handleStatChange}
            disabled={selectedStats.length === 2 && !selectedStats.includes("fieldGoalsMade")}
          />
          Field Goals Made
        </label>
        <label>
          <input
            type="checkbox"
            value="threePointsMade"
            onChange={handleStatChange}
            disabled={selectedStats.length === 2 && !selectedStats.includes("threePointsMade")}
          />
          3P Made
        </label>
      </div>

      <button onClick={handleToggleStats}>
        {isSeasonal ? 'Show Game-by-Game Stats' : 'Show Seasonal Stats'}
      </button>

      <div>
          <Plot
            data={plotData}
            layout={layout}
          />
      </div>
    </div>
  );
}

export default StatsGraph;
