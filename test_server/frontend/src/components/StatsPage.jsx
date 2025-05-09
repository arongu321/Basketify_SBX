import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import { useParams, useNavigate } from 'react-router-dom';
import logo from '../assets/Basketify-Logo.png';
import FilterSection from './FilterSection';
import '../styles/StatsPage.css';

// FR25, FR26, FR27, FR28 - Component that displays statistics with filter functionality
function StatsPage() {
    const { type, name } = useParams();
    const navigate = useNavigate();
    const [statsData, setStatsData] = useState([]);
    const [seasonalStats, setSeasonalStats] = useState([]);
    const [historyStats, setHistoryStats] = useState([]);
    const [futureGames, setFutureGames] = useState([]);
    const [isSeasonal, setIsSeasonal] = useState(false);
    const [loading, setLoading] = useState(true);
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [activeFilters, setActiveFilters] = useState({});
    const [isFiltered, setIsFiltered] = useState(false);

    // FR26, FR28 - Fetches stats with optional filter parameters
    const fetchStats = async (filters = {}) => {
        setLoading(true);
        try {
            // FR26 - Construct the URL with query parameters for filtering
            let url = `/api/stats/${type}/${name}`;

            // FR26 - Add filter parameters to the URL if they exist
            if (Object.keys(filters).length > 0) {
                const queryParams = new URLSearchParams(filters);
                url += `?${queryParams.toString()}`;
                setIsFiltered(true);
            } else {
                // FR28 - Reset filtered status when no filters are applied
                setIsFiltered(false);
            }

            const response = await api.get(url);
            const { stats, seasonal_stats } = response.data;

            // Set all the data
            setStatsData(stats);
            setSeasonalStats(seasonal_stats);

            // Separate future games from historical games
            const futureGames = stats.filter((stat) => stat.is_future_game);
            const historical = stats.filter((stat) => !stat.is_future_game);

            setHistoryStats(historical);
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

    // FR26, FR27, FR28 - Handle filter application from FilterSection component
    const handleApplyFilters = (filters, isClearOperation = false) => {
        setActiveFilters(filters);

        // FR26, FR28 - Only make API call if there are filters or if this is a clear operation
        // when clearing filters and no filters were active before, no need to reload
        if (
            Object.keys(filters).length > 0 ||
            (Object.keys(activeFilters).length > 0 && isClearOperation)
        ) {
            fetchStats(filters);
        } else if (isClearOperation) {
            // FR28 - Just update the filter status without making API call
            setIsFiltered(false);
        }
    };

    const handleToggleStats = () => {
        setIsSeasonal(!isSeasonal);
    };

    const handleGoToGraph = () => {
        navigate(`/stats-graph/${type}/${name}`);
    };

    // FR25 - Toggle filter panel visibility
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

    // FR25, FR26 - Display filter status to show user which filters are active
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

        // Month filter
        const month = activeFilters.month || '';
        if (month) {
            const monthNames = [
                'January',
                'February',
                'March',
                'April',
                'May',
                'June',
                'July',
                'August',
                'September',
                'October',
                'November',
                'December',
            ];
            filterMessages.push(`Month: ${monthNames[parseInt(month) - 1]}`);
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

        // Create human-readable messages for each active filter
        // Date filters
        // Month filter
        // Last N Games
        // Season
        // Season Type
        // Conference
        // Division
        // Game Type
        // Outcome
        // Opponents

        // FR26 - Return visual indicator of active filters
        return (
            <div className="filter-status">
                <span>Filtering: {filterMessages.join(' • ')}</span>
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

                    {/* FR25 - Button to toggle filter panel visibility */}
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

                {/* FR25 - Render filter panel when open */}
                <FilterSection
                    isOpen={isFilterOpen}
                    onApplyFilters={handleApplyFilters}
                    entityType={type}
                    initialFilters={activeFilters}
                />

                {/* FR26 - Display active filter status */}
                {renderFilterStatus()}

                {statsData.length === 0 ? (
                    <p>No stats available for this {type}.</p>
                ) : (
                    <div>
                        {/* Display Future Games First */}
                        {!isSeasonal && futureGames.length > 0 && (
                            <>
                                <h2>Upcoming Games (Predictions)</h2>
                                <table className="stats-page-table">
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Opponent</th>
                                            <th>Predicted Outcome</th>
                                            <th>Location</th>
                                            <th>Season Type</th>
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
                                                            .replace(/-/g, '/')
                                                            .replace(/T.+/, '')
                                                    ).toLocaleDateString()}
                                                </td>
                                                <td>
                                                    {gameStats.opponent ||
                                                        'N/A'}
                                                </td>
                                                <td>{gameStats.WinLoss}</td>
                                                <td>
                                                    {gameStats.gameLocation}
                                                </td>
                                                <td>{gameStats.seasonType}</td>
                                                <td>{gameStats.points}</td>
                                                <td>{gameStats.rebounds}</td>
                                                <td>{gameStats.assists}</td>
                                                <td>
                                                    {gameStats.fieldGoalsMade}
                                                </td>
                                                <td>
                                                    {gameStats.fieldGoalPercentage
                                                        ? (
                                                              gameStats.fieldGoalPercentage *
                                                              100
                                                          ).toFixed(1)
                                                        : 'N/A'}
                                                    %
                                                </td>
                                                <td>
                                                    {gameStats.threePointsMade}
                                                </td>
                                                <td>
                                                    {gameStats.threePointPercentage
                                                        ? (
                                                              gameStats.threePointPercentage *
                                                              100
                                                          ).toFixed(1)
                                                        : 'N/A'}
                                                    %
                                                </td>
                                                <td>
                                                    {gameStats.freeThrowsMade}
                                                </td>
                                                <td>
                                                    {gameStats.freeThrowPercentage
                                                        ? (
                                                              gameStats.freeThrowPercentage *
                                                              100
                                                          ).toFixed(1)
                                                        : 'N/A'}
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

                        {/* Then Display Historical Games */}
                        <h2>
                            {!isSeasonal && futureGames.length > 0
                                ? 'Past Games'
                                : 'All Games'}
                        </h2>
                        <table className="stats-page-table">
                            <thead>
                                <tr>
                                    <th>{isSeasonal ? 'Season' : 'Date'}</th>
                                    {!isSeasonal && <th>Opponent</th>}
                                    {!isSeasonal && <th>Game Outcome</th>}
                                    {!isSeasonal && <th>Location</th>}
                                    {!isSeasonal && <th>Season Type</th>}
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
                                {(isSeasonal ? seasonalStats : historyStats) // Use all historical stats instead of currentSeasonStats
                                    .slice()
                                    .reverse()
                                    .map((gameStats, index) => (
                                        <tr key={index}>
                                            <td>
                                                {isSeasonal
                                                    ? gameStats.season
                                                    : new Date(
                                                          gameStats.date
                                                              .replace(
                                                                  /-/g,
                                                                  '/'
                                                              )
                                                              .replace(
                                                                  /T.+/,
                                                                  ''
                                                              )
                                                      ).toLocaleDateString()}
                                            </td>
                                            {!isSeasonal && (
                                                <td>
                                                    {gameStats.opponent ||
                                                        'N/A'}
                                                </td>
                                            )}
                                            {!isSeasonal && (
                                                <td>{gameStats.WinLoss}</td>
                                            )}
                                            {!isSeasonal && (
                                                <td>
                                                    {gameStats.gameLocation}
                                                </td>
                                            )}
                                            {!isSeasonal && (
                                                <td>{gameStats.seasonType}</td>
                                            )}
                                            <td>
                                                {gameStats.points
                                                    ? gameStats.points.toFixed(
                                                          0
                                                      )
                                                    : 'N/A'}
                                            </td>
                                            <td>
                                                {gameStats.rebounds
                                                    ? gameStats.rebounds.toFixed(
                                                          0
                                                      )
                                                    : 'N/A'}
                                            </td>
                                            <td>
                                                {gameStats.assists
                                                    ? gameStats.assists.toFixed(
                                                          0
                                                      )
                                                    : 'N/A'}
                                            </td>
                                            <td>
                                                {gameStats.fieldGoalsMade
                                                    ? gameStats.fieldGoalsMade.toFixed(
                                                          0
                                                      )
                                                    : 'N/a'}
                                            </td>
                                            <td>
                                                {gameStats.fieldGoalPercentage
                                                    ? (
                                                          gameStats.fieldGoalPercentage *
                                                          100
                                                      ).toFixed(1)
                                                    : 'N/A'}
                                                %
                                            </td>
                                            <td>
                                                {gameStats.threePointsMade
                                                    ? gameStats.threePointsMade.toFixed(
                                                          0
                                                      )
                                                    : 'N/A'}
                                            </td>
                                            <td>
                                                {gameStats.threePointPercentage
                                                    ? (
                                                          gameStats.threePointPercentage *
                                                          100
                                                      ).toFixed(1)
                                                    : 'N/A'}
                                                %
                                            </td>
                                            <td>
                                                {gameStats.freeThrowsMade
                                                    ? gameStats.freeThrowsMade.toFixed(
                                                          0
                                                      )
                                                    : 'N/A'}
                                            </td>
                                            <td>
                                                {gameStats.freeThrowPercentage
                                                    ? (
                                                          gameStats.freeThrowPercentage *
                                                          100
                                                      ).toFixed(1)
                                                    : 'N/A'}
                                                %
                                            </td>
                                            <td>
                                                {gameStats.steals
                                                    ? gameStats.steals.toFixed(
                                                          0
                                                      )
                                                    : 'N/A'}
                                            </td>
                                            <td>
                                                {gameStats.blocks
                                                    ? gameStats.blocks.toFixed(
                                                          0
                                                      )
                                                    : 'N/A'}
                                            </td>
                                            <td>
                                                {gameStats.turnovers
                                                    ? gameStats.turnovers.toFixed(
                                                          0
                                                      )
                                                    : 'N/A'}
                                            </td>
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
