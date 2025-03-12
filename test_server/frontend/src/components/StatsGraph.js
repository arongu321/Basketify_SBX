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

      setCurrentSeasonStats(currentSeason);
    }
  }, [statsData]);

  const handleStatChange = (event) => {
    const stat = event.target.value;
    setSelectedStats(prevStats => {
      if (prevStats.includes(stat)) {
        return prevStats.filter(item => item !== stat);
      } else {
        const newStats = [...prevStats, stat];
        // ensure we never exceed 2 stats
        return newStats.length > 2 ? newStats.slice(1) : newStats;
      }
    });
  };

  const handleToggleStats = () => {
    setIsSeasonal(!isSeasonal);
  };

  if (loading) return <div>Loading...</div>;

  const plotData = selectedStats.map((stat, index) => {
    const dataToUse = isSeasonal ? seasonalStats.slice().reverse() : currentSeasonStats;
    const xValues = dataToUse.map((data) => 
      isSeasonal ? data.season : new Date(data.date).toLocaleDateString()
    );
    const yValues = dataToUse.map((data) => 
      data[stat] || 0
    );

    const formattedStatName = stat.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());

    return {
      type: 'scatter',
      mode: 'lines+markers',
      name: formattedStatName,
      x: xValues,
      y: yValues,
      yaxis: index === 1 ? 'y2' : 'y',
    };
  });

  const layout = {
    title: 'Stats Over Time',
    xaxis: { title: isSeasonal ? 'Season' : 'Date' },
    yaxis: {
      title: {
        text: selectedStats[0] ? selectedStats[0].replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()) : '',
        font: {
          size: 20,
          color: '#7f7f7f'
        }
      },
      side: 'left',
      range: selectedStats.length > 0 ? [
        0,
        Math.max(...(isSeasonal ? seasonalStats.slice().reverse() : currentSeasonStats).map((data) => data[selectedStats[0]] || 0)) * 1.2
      ] : undefined
    },
    ...(selectedStats.length === 2 && {
      yaxis2: {
        title: {
          text: selectedStats[1] ? selectedStats[1].replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()) : '',
          font: {
            size: 20,
            color: '#7f7f7f'
          }
        },
        side: 'right',
        overlaying: 'y',
        range: [
          0,
          Math.max(...(isSeasonal ? seasonalStats.slice().reverse() : currentSeasonStats).map((data) => data[selectedStats[1]] || 0)) * 1.2
        ]
      }
    })
  };

  return (
    <div>
      <h1>Stats Graph: {type.charAt(0).toUpperCase() + type.slice(1)} - {name}</h1>

      <div>
        <h3>Select stats to plot:</h3>
        {['points', 'rebounds', 'assists', 'fieldGoalsMade', 'threePointsMade', 'fieldGoalPercentage', 'threePointPercentage', 'freeThrowsMade', 'freeThrowPercentage', 'steals', 'blocks', 'turnovers'].map(stat => (
          <label key={stat}>
            <input
              type="checkbox"
              value={stat}
              checked={selectedStats.includes(stat)}
              onChange={handleStatChange}
              disabled={selectedStats.length === 2 && !selectedStats.includes(stat)}
            />
            {stat === 'points' ? 'Points Scored' : 
            stat === 'rebounds' ? 'Rebounds' : 
            stat === 'assists' ? 'Assists' : 
            stat === 'fieldGoalsMade' ? 'Field Goals Made' :
            stat === 'threePointsMade' ? '3P Made' :
            stat === 'fieldGoalPercentage' ? 'Field Goal %' :
            stat === 'threePointPercentage' ? '3P %' :
            stat === 'freeThrowsMade' ? 'Free Throws Made' :
            stat === 'freeThrowPercentage' ? 'Free Throw %' :
            stat === 'steals' ? 'Steals' :
            stat === 'blocks' ? 'Blocks' :
            stat === 'turnovers' ? 'Turnovers' : stat}
          </label>
        ))}
      </div>


      <button onClick={handleToggleStats}>
        {isSeasonal ? 'Show Game-by-Game Stats' : 'Show Seasonal Stats'}
      </button>

      {selectedStats.length > 0 && (
        <div>
          <Plot
            data={plotData}
            layout={layout}
            style={{ width: '100%', height: '600px' }}
          />
        </div>
      )}
    </div>
  );
}

export default StatsGraph;
