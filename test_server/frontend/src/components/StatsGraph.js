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
        const newStats = [...prevStats, stat];
        // Ensure we never exceed 2 stats
        return newStats.length > 2 ? newStats.slice(1) : newStats;
      }
    });
  };

  const handleToggleStats = () => {
    setIsSeasonal(!isSeasonal);
  };

  if (loading) return <div>Loading...</div>;

  const dataSource = isSeasonal ? seasonalStats : currentSeasonStats;

  const plotData = selectedStats.map((stat, index) => {
    const xValues = dataSource.map((data) => 
      isSeasonal ? data.season : new Date(data.date).toLocaleDateString()
    );
    const yValues = dataSource.map((data) => 
      data[stat] || 0
    );

    return {
      type: 'scatter',
      mode: 'lines+markers',
      name: stat,
      x: xValues,
      y: yValues,
      yaxis: index === 1 ? 'y2' : 'y',
    };
  });

  
  const layout = {
    title: 'Stats Over Time',
    xaxis: { title: isSeasonal ? 'Season' : 'Date' },
    yaxis: {
      title: selectedStats[0] || '',
      side: 'left',
      range: selectedStats.length > 0 ? [
        0,
        Math.max(
          ...dataSource.map((data) => 
            data[selectedStats[0]?.toLowerCase().replace(' ', '')] || 0
          )
        )
      ] : undefined
    },
    ...(selectedStats.length === 2 && {
      yaxis2: {
        title: selectedStats[1],
        side: 'right',
        overlaying: 'y',
        range: [
          0,
          Math.max(
            ...dataSource.map((data) => 
              data[selectedStats[1].toLowerCase().replace(' ', '')] || 0
            )
          )
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
