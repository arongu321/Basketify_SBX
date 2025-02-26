import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'; 
import Plot from 'react-plotly.js';
import axios from 'axios';

function StatsGraph() {
  const { type, name } = useParams();
  const [statsData, setStatsData] = useState([]);
  const [selectedStats, setSelectedStats] = useState([]);
  const [loading, setLoading] = useState(true);

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

  const handleStatChange = (event) => {
    const stat = event.target.value;
    if (selectedStats.includes(stat)) {
      setSelectedStats(selectedStats.filter(item => item !== stat));
    } else {
      if (selectedStats.length < 2) {
        setSelectedStats([...selectedStats, stat]);
      }
    }
  };

  if (loading) return <div>Loading...</div>;

  // Prepare data for plotting
  const plotData = selectedStats.map(stat => {
    const xValues = statsData.map(data => data.year);
    const yValues = statsData.map(data => data[stat.toLowerCase().replace(' ', '')]);
    return {
      type: 'scatter',
      mode: 'lines+markers',
      name: stat,
      x: xValues,
      y: yValues,
    };
  });

  return (
    <div>
      <h1>Stats Graph: {type.charAt(0).toUpperCase() + type.slice(1)} - {name}</h1>
      
      <div>
        <h3>Select stats to plot:</h3>
        <label>
          <input 
            type="checkbox" 
            value="Points Scored" 
            onChange={handleStatChange}
          /> Points Scored
        </label>
        <label>
          <input 
            type="checkbox" 
            value="Rebounds" 
            onChange={handleStatChange}
          /> Rebounds
        </label>
        <label>
          <input 
            type="checkbox" 
            value="Assists" 
            onChange={handleStatChange}
          /> Assists
        </label>
        <label>
          <input 
            type="checkbox" 
            value="Field Goals Made" 
            onChange={handleStatChange}
          /> Field Goals Made
        </label>
        <label>
          <input 
            type="checkbox" 
            value="3P Made" 
            onChange={handleStatChange}
          /> 3P Made
        </label>
        {/* Add more checkboxes for other stats if needed */}
      </div>

      <div>
        {selectedStats.length > 0 && (
          <Plot
            data={plotData}
            layout={{
              title: 'Stats Over Time',
              xaxis: { title: 'Year' },
              yaxis: { title: 'Value' },
            }}
          />
        )}
      </div>
    </div>
  );
}

export default StatsGraph;
