/*
Frontend JS (+ dynamically returned HTML) for graph of statistics.
Fulfills FR11, FR12, FR13, FR14, FR15, FR18
*/

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import api from '../utils/api';
import logo from '../assets/Basketify-Logo.png';
import '../styles/StatsGraph.css';

function StatsGraph() {
    const { type, name } = useParams();
    const navigate = useNavigate();
    const [statsData, setStatsData] = useState([]);
    const [futureGames, setFutureGames] = useState([]);
    const [seasonalStats, setSeasonalStats] = useState([]);
    const [currentSeasonStats, setCurrentSeasonStats] = useState([]);
    const [selectedStats, setSelectedStats] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isSeasonal, setIsSeasonal] = useState(false);

    // get player / teams stats (complete: i.e. all stats for this player/team, game-by-game and seasonal): all of FR11-FR15
    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get(`/api/stats/${type}/${name}`);
                setStatsData(response.data.stats);
                setSeasonalStats(response.data.seasonal_stats);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching stats data:', error);
                setLoading(false);
            }
        };

        fetchStats();
    }, [type, name]);

    // get stats of games for current season + split off future games, FR11
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

                return (
                    statDate >= seasonStart &&
                    statDate <= seasonEnd &&
                    !stat.is_future_game
                );
            });

            setCurrentSeasonStats(currentSeason);

            const futureGames = statsData.filter((stat) => stat.is_future_game);
            setFutureGames(futureGames);
        }
    }, [statsData]);

    // handle click on stat button: can select up to 2 at a time. FR12 and FR13
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

    // toggle game-by-game or seasonal button: FR15
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

    // set up plot of data: FR11
    const plotData = selectedStats
        .map((stat, index) => {
            const dataSource = isSeasonal
                ? seasonalStats
                : currentSeasonStats; // reverse so most recent is at end of array (display on right side)

            const currentSeasonX = dataSource.map((data) =>
                isSeasonal
                    ? data.season
                    : new Date(data.date).toLocaleDateString()
            );
            const currentSeasonY = dataSource.map((data) => data[stat] || 0);

            const formattedStatName = stat
                .replace(/([A-Z])/g, ' $1')
                .replace(/^./, (str) => str.toUpperCase());

            const colors = ['blue', 'green', 'orange', 'purple', 'red', 'cyan'];
            const currentColor = colors[index % colors.length];
            const futureColor = colors[(index + 2) % colors.length];

            const traces = [
                {
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: `${formattedStatName} (${
                        isSeasonal ? 'Seasons' : 'Current Season'
                    })`,
                    x: currentSeasonX,
                    y: currentSeasonY,
                    line: { color: currentColor },
                    marker: { color: currentColor },
                    yaxis: index === 0 ? 'y1' : 'y2',
                },
            ];

            // Only add future games if not in seasonal mode. Future games are ML predictions: FR18
            if (!isSeasonal) {
                const futureGamesX = futureGames.map((data) =>
                    new Date(data.date).toLocaleDateString()
                );
                const futureGamesY = futureGames.map((data) => data[stat] || 0);

                traces.push({
                    type: 'scatter',
                    mode: 'markers',
                    name: `${formattedStatName} (Future Games)`,
                    x: futureGamesX,
                    y: futureGamesY,
                    marker: { color: futureColor, symbol: 'star' },
                    yaxis: index === 0 ? 'y1' : 'y2',
                });
            }

            return traces;
        })
        .flat();

    // Display graph of stats: FR11, use Plotly to make graph hoverable: FR14
    const layout = {
        title: 'Stats Over Time',
        xaxis: {
            title: isSeasonal ? 'Season' : 'Date',
            type: 'category',
            tickvals: !isSeasonal
                ? currentSeasonStats
                    .map((data, idx) => idx)
                    .filter((_, i) => i % 5 === 0) // show every 5th tick
                : undefined,
            ticktext: !isSeasonal
                ? currentSeasonStats
                    .map((data) => new Date(data.date).toLocaleDateString())
                    .filter((_, i) => i % 5 === 0)
                : undefined,
                },
        yaxis: {
            title: {
                text: selectedStats[0]
                    ? selectedStats[0]
                          .replace(/([A-Z])/g, ' $1')
                          .replace(/^./, (str) => str.toUpperCase())
                    : '',
                font: {
                    size: 20,
                    color: '#7f7f7f',
                },
            },
            side: 'left',
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
        yaxis2: {
            title: {
                text: selectedStats[1]
                    ? selectedStats[1]
                          .replace(/([A-Z])/g, ' $1')
                          .replace(/^./, (str) => str.toUpperCase())
                    : '',
                font: {
                    size: 20,
                    color: '#7f7f7f',
                },
            },
            side: 'right',
            overlaying: 'y',
            range:
                selectedStats.length > 1
                    ? [
                          0,
                          Math.max(
                              ...(isSeasonal
                                  ? seasonalStats.slice().reverse()
                                  : currentSeasonStats
                              ).map((data) => data[selectedStats[1]] || 0)
                          ) * 1.2,
                      ]
                    : undefined,
        },
        height: 650,
        width: 1200,
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
                        Stats Graph:{' '}
                        {type.charAt(0).toUpperCase() + type.slice(1)} - {name}
                    </h1>
                </div>
            </div>

            <div className="stats-graph-selection-div">
                <h3>
                    Select stats to plot (you can select up to 2 at a time):
                </h3>
                <div className="stats-graph-button-container">
                    {[
                        'points',
                        'rebounds',
                        'assists',
                        'fieldGoalsMade',
                        'threePointsMade',
                        'fieldGoalPercentage',
                        'threePointPercentage',
                        'freeThrowsMade',
                        'freeThrowPercentage',
                        'steals',
                        'blocks',
                        'turnovers',
                    ].map((stat) => (
                        <button
                            key={stat}
                            value={stat}
                            onClick={() =>
                                handleStatChange({ target: { value: stat } })
                            }
                            className={
                                selectedStats.includes(stat)
                                    ? 'stats-graph-button active'
                                    : 'stats-graph-button'
                            }
                            disabled={
                                selectedStats.length === 2 &&
                                !selectedStats.includes(stat)
                            }
                        >
                            {stat
                                .replace(/([A-Z])/g, ' $1')
                                .replace(/^./, (str) => str.toUpperCase())}
                        </button>
                    ))}
                </div>
                <button
                    className="stats-graph-seasonal-stats-button"
                    onClick={handleToggleStats}
                >
                    {isSeasonal
                        ? 'Show Game-by-Game Stats'
                        : 'Show Seasonal Stats'}
                </button>
            </div>

            <div className="stats-graph-content">
                {selectedStats.length > 0 && (
                    <div className="stats-graph-container-inner">
                        <Plot
                            data={plotData}
                            layout={layout}
                            config={{ responsive: true }}
                        />
                    </div>
                )}
            </div>

            <div className="bottom-banner"></div>
        </div>
    );
}

export default StatsGraph;
