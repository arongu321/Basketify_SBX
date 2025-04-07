import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import logo from '../assets/Basketify-Logo.png';
import FilterSection from './FilterSection';
import '../styles/StatsPage.css';

function StatsPage() {
    const { type, name } = useParams();
    const navigate = useNavigate();
    const [statsData, setStatsData] = useState([]);
    const [seasonalStats, setSeasonalStats] = useState([]);
    const [currentSeasonStats, setCurrentSeasonStats] = useState([]);
    const [futureGames, setFutureGames] = useState([]);
    const [isSeasonal, setIsSeasonal] = useState(false);
    const [loading, setLoading] = useState(true);
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [activeFilters, setActiveFilters] = useState({});
    const [isFiltered, setIsFiltered] = useState(false);

    const fetchStats = async (filters = {}) => {
        setLoading(true);
        try {
            // Construct the URL with query parameters for filtering
            let url = `http://localhost:8000/api/stats/${type}/${name}`;

            // Add filter parameters to the URL if they exist
            if (Object.keys(filters).length > 0) {
                const queryParams = new URLSearchParams(filters);
                url += `?${queryParams.toString()}`;
                setIsFiltered(true);
            } else {
                setIsFiltered(false);
            }

            const response = await axios.get(url);
            const { stats, seasonal_stats } = response.data;

            // Process current season stats
            const currentSeason = stats.filter((stat) => {
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

            const futureGames = stats.filter((stat) => stat.is_future_game);

            setStatsData(stats);
            setSeasonalStats(seasonal_stats);
            setCurrentSeasonStats(currentSeason);
            setFutureGames(futureGames);
        } catch (error) {
            console.error('Error fetching stats data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, [type, name]);

    const handleApplyFilters = (filters, isClearOperation = false) => {
        setActiveFilters(filters);

        // Only make API call if there are filters or if this isn't a clear operation
        // when clearing filters and no filters were active before, no need to reload
        if (
            Object.keys(filters).length > 0 ||
            (Object.keys(activeFilters).length > 0 && isClearOperation)
        ) {
            fetchStats(filters);
        } else if (isClearOperation) {
            // Just update the filter status without making API call
            setIsFiltered(false);
        }
    };

    const handleToggleStats = () => {
        setIsSeasonal(!isSeasonal);
    };

    const handleGoToGraph = () => {
        navigate(`/stats-graph/${type}/${name}`);
    };

    const toggleFilter = () => {
        setIsFilterOpen(!isFilterOpen);
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

    // Display filter status
    const renderFilterStatus = () => {
        if (!isFiltered) return null;

        const filterMessages = [];

        // Date filters
        const dateFrom = activeFilters.date_from || '';
        const dateTo = activeFilters.date_to || '';
        if (dateFrom && dateTo) {
            filterMessages.push(`Date range: ${dateFrom} to ${dateTo}`);
        } else if (dateFrom) {
            filterMessages.push(`From date: ${dateFrom}`);
        } else if (dateTo) {
            filterMessages.push(`To date: ${dateTo}`);
        }

        // Last N Games
        const lastNGames = activeFilters.last_n_games || '';
        if (lastNGames) {
            filterMessages.push(`Last ${lastNGames} games`);
        }

        // Season
        if (activeFilters.season) {
            filterMessages.push(`Season: ${activeFilters.season}`);
        }

        // Season Type
        if (activeFilters.season_type) {
            filterMessages.push(`Season Type: ${activeFilters.season_type}`);
        }

        // Conference
        if (activeFilters.conference) {
            filterMessages.push(`Conference: ${activeFilters.conference}`);
        }

        // Division
        if (activeFilters.division) {
            filterMessages.push(`Division: ${activeFilters.division}`);
        }

        // Game Type
        if (activeFilters.game_type && activeFilters.game_type !== 'All') {
            filterMessages.push(`Game Type: ${activeFilters.game_type}`);
        }

        // Outcome
        if (activeFilters.outcome && activeFilters.outcome !== 'All') {
            filterMessages.push(`Outcome: ${activeFilters.outcome}`);
        }

        // Opponents
        if (activeFilters.opponents) {
            const opponentsList = activeFilters.opponents.split(',');
            if (opponentsList.length > 2) {
                filterMessages.push(
                    `Opponents: ${opponentsList.length} teams selected`
                );
            } else {
                filterMessages.push(
                    `Opponents: ${activeFilters.opponents.replace(/,/g, ', ')}`
                );
            }
        }

        return (
            <div className="filter-status">
                <span>Filtering: {filterMessages.join(' • ')}</span>
                <button
                    className="clear-filter-button"
                    onClick={() => handleApplyFilters({}, true)}
                >
                    Clear
                </button>
            </div>
        );
    };

    return (
        <div className="stats-page-container">
            <div className="stats-page-top-banner">
                <button
                    className="stats-page-back-button"
                    onClick={() => navigate(-1)}
                >
                    Back
                </button>
                <div className="stats-page-header-content">
                    <h1 className="stats-page-title">
                        {type.charAt(0).toUpperCase() + type.slice(1)} Stats:{' '}
                        {name}
                    </h1>
                </div>
            </div>

            <div className="stats-page-content">
                <div className="stats-page-button-container">
                    <button onClick={handleToggleStats}>
                        {isSeasonal
                            ? 'Show Game-by-Game Stats'
                            : 'Show Seasonal Stats'}
                    </button>
                    <button onClick={handleGoToGraph}>View Stats Graph</button>
                    <button
                        onClick={toggleFilter}
                        className={
                            isFilterOpen
                                ? 'active-filter-button filter-button'
                                : 'filter-button'
                        }
                    >
                        {isFilterOpen ? 'Hide Filters' : 'Filter'}
                    </button>
                </div>

                {!isSeasonal && (
                    <FilterSection
                        isOpen={isFilterOpen}
                        onApplyFilters={handleApplyFilters}
                        entityType={type}
                    />
                )}

                {renderFilterStatus()}

                {statsData.length === 0 ? (
                    <p>No stats available for this {type}.</p>
                ) : (
                    <div>
                        <table className="stats-page-table">
                            <thead>
                                <tr>
                                    <th>{isSeasonal ? 'Season' : 'Date'}</th>
                                    {!isSeasonal && <th>Opponent</th>}
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
                                {(isSeasonal
                                    ? seasonalStats
                                    : currentSeasonStats
                                )
                                    .slice()
                                    .reverse()
                                    .map((gameStats, index) => (
                                        <tr key={index}>
                                            <td>
                                                {isSeasonal
                                                    ? gameStats.season
                                                    : new Date(
                                                          gameStats.date
                                                      ).toLocaleDateString()}
                                            </td>
                                            {!isSeasonal && (
                                                <td>
                                                    {gameStats.opponent ||
                                                        'N/A'}
                                                </td>
                                            )}
                                            <td>{gameStats.points}</td>
                                            <td>{gameStats.rebounds}</td>
                                            <td>{gameStats.assists}</td>
                                            <td>{gameStats.fieldGoalsMade}</td>
                                            <td>
                                                {(
                                                    gameStats.fieldGoalPercentage *
                                                    100
                                                ).toFixed(1)}
                                                %
                                            </td>
                                            <td>{gameStats.threePointsMade}</td>
                                            <td>
                                                {(
                                                    gameStats.threePointPercentage *
                                                    100
                                                ).toFixed(1)}
                                                %
                                            </td>
                                            <td>{gameStats.freeThrowsMade}</td>
                                            <td>
                                                {(
                                                    gameStats.freeThrowPercentage *
                                                    100
                                                ).toFixed(1)}
                                                %
                                            </td>
                                            <td>{gameStats.steals}</td>
                                            <td>{gameStats.blocks}</td>
                                            <td>{gameStats.turnovers}</td>
                                        </tr>
                                    ))}
                            </tbody>
                        </table>

                        {!isSeasonal && futureGames.length > 0 && (
                            <>
                                <h2>Future Games</h2>
                                <table className="stats-page-table">
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Opponent</th>
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
                                                <td>
                                                    {new Date(
                                                        gameStats.date
                                                    ).toLocaleDateString()}
                                                </td>
                                                <td>
                                                    {gameStats.opponent ||
                                                        'N/A'}
                                                </td>
                                                <td>{gameStats.points}</td>
                                                <td>{gameStats.rebounds}</td>
                                                <td>{gameStats.assists}</td>
                                                <td>
                                                    {gameStats.fieldGoalsMade}
                                                </td>
                                                <td>
                                                    {(
                                                        gameStats.fieldGoalPercentage *
                                                        100
                                                    ).toFixed(1)}
                                                    %
                                                </td>
                                                <td>
                                                    {gameStats.threePointsMade}
                                                </td>
                                                <td>
                                                    {(
                                                        gameStats.threePointPercentage *
                                                        100
                                                    ).toFixed(1)}
                                                    %
                                                </td>
                                                <td>
                                                    {gameStats.freeThrowsMade}
                                                </td>
                                                <td>
                                                    {(
                                                        gameStats.freeThrowPercentage *
                                                        100
                                                    ).toFixed(1)}
                                                    %
                                                </td>
                                                <td>{gameStats.steals}</td>
                                                <td>{gameStats.blocks}</td>
                                                <td>{gameStats.turnovers}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </>
                        )}
                    </div>
                )}
            </div>

            <div className="stats-page-bottom-banner"></div>
        </div>
    );
}

export default StatsPage;
