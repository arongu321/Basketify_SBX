import React, { useState } from 'react';
import '../styles/FilterSection.css';
import {
    NBA_SEASONS,
    SEASON_TYPES,
    NBA_DIVISIONS,
    NBA_CONFERENCES,
    GAME_TYPES,
    GAME_OUTCOMES,
    NBA_TEAMS,
} from '../utils/constants';

const FilterSection = ({ isOpen, onApplyFilters, entityType }) => {
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');
    const [lastNGames, setLastNGames] = useState('');

    // New filter states
    const [selectedSeason, setSelectedSeason] = useState('');
    const [selectedSeasonType, setSelectedSeasonType] = useState('');
    const [selectedDivision, setSelectedDivision] = useState('');
    const [selectedConference, setSelectedConference] = useState('');
    const [selectedGameType, setSelectedGameType] = useState('');
    const [selectedOutcome, setSelectedOutcome] = useState('');
    const [selectedOpponents, setSelectedOpponents] = useState([]);

    const handleApplyFilters = () => {
        // Construct query parameters for backend filtering
        const filters = {};

        // Original filters
        if (dateFrom) filters.date_from = dateFrom;
        if (dateTo) filters.date_to = dateTo;
        if (lastNGames) filters.last_n_games = lastNGames;

        // New filters
        if (selectedSeason) filters.season = selectedSeason;
        if (selectedSeasonType && selectedSeasonType !== 'All')
            filters.season_type = selectedSeasonType;
        if (selectedDivision && selectedDivision !== 'All')
            filters.division = selectedDivision;
        if (selectedConference && selectedConference !== 'All')
            filters.conference = selectedConference;
        if (selectedGameType && selectedGameType !== 'All')
            filters.game_type = selectedGameType;
        if (selectedOutcome && selectedOutcome !== 'All')
            filters.outcome = selectedOutcome;
        if (selectedOpponents.length > 0)
            filters.opponents = selectedOpponents.join(',');

        // Pass the filters to the parent component
        onApplyFilters(filters);
    };

    const handleClearFilters = () => {
        // Reset all filter states
        setDateFrom('');
        setDateTo('');
        setLastNGames('');
        setSelectedSeason('');
        setSelectedSeasonType('');
        setSelectedDivision('');
        setSelectedConference('');
        setSelectedGameType('');
        setSelectedOutcome('');
        setSelectedOpponents([]);

        // Clear filters in parent component
        onApplyFilters({}, true);
    };

    const toggleOpponent = (team) => {
        setSelectedOpponents((prev) =>
            prev.includes(team)
                ? prev.filter((t) => t !== team)
                : [...prev, team]
        );
    };

    if (!isOpen) return null;

    return (
        <div className="filter-section">
            <h3>Filter Options</h3>
            <div className="filter-content">
                {/* Original date range filters */}
                <div className="filter-group">
                    <label>Date Range:</label>
                    <div className="filter-controls">
                        <input
                            type="date"
                            placeholder="Start Date"
                            value={dateFrom}
                            onChange={(e) => setDateFrom(e.target.value)}
                        />
                        <span>to</span>
                        <input
                            type="date"
                            placeholder="End Date"
                            value={dateTo}
                            onChange={(e) => setDateTo(e.target.value)}
                        />
                    </div>
                </div>

                {/* Season selector */}
                <div className="filter-group">
                    <label>Season:</label>
                    <div className="filter-controls">
                        <select
                            value={selectedSeason}
                            onChange={(e) => setSelectedSeason(e.target.value)}
                        >
                            <option value="">All Seasons</option>
                            {NBA_SEASONS.map((season) => (
                                <option key={season} value={season}>
                                    {season}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Season type filter */}
                <div className="filter-group">
                    <label>Season Type:</label>
                    <div className="filter-controls">
                        <select
                            value={selectedSeasonType}
                            onChange={(e) =>
                                setSelectedSeasonType(e.target.value)
                            }
                        >
                            <option value="">All Types</option>
                            {SEASON_TYPES.map((type) => (
                                <option key={type} value={type}>
                                    {type}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Game outcome filter */}
                <div className="filter-group">
                    <label>Game Outcome:</label>
                    <div className="filter-controls">
                        <select
                            value={selectedOutcome}
                            onChange={(e) => setSelectedOutcome(e.target.value)}
                        >
                            {GAME_OUTCOMES.map((outcome) => (
                                <option key={outcome} value={outcome}>
                                    {outcome}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Last N Games filter */}
                <div className="filter-group">
                    <label>Last N Games:</label>
                    <div className="filter-controls">
                        <input
                            type="number"
                            placeholder="Enter number of games"
                            min="1"
                            max="100"
                            value={lastNGames}
                            onChange={(e) => setLastNGames(e.target.value)}
                        />
                        <span className="filter-help-text">
                            Show only the most recent games
                        </span>
                    </div>
                </div>

                {/* Conference filter */}
                <div className="filter-group">
                    <label>Conference:</label>
                    <div className="filter-controls">
                        <select
                            value={selectedConference}
                            onChange={(e) =>
                                setSelectedConference(e.target.value)
                            }
                        >
                            <option value="">All Conferences</option>
                            {NBA_CONFERENCES.map((conf) => (
                                <option key={conf} value={conf}>
                                    {conf}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Division filter */}
                <div className="filter-group">
                    <label>Division:</label>
                    <div className="filter-controls">
                        <select
                            value={selectedDivision}
                            onChange={(e) =>
                                setSelectedDivision(e.target.value)
                            }
                        >
                            <option value="">All Divisions</option>
                            {NBA_DIVISIONS.map((div) => (
                                <option key={div} value={div}>
                                    {div}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Game type filter (Inter/Intra conference) */}
                <div className="filter-group">
                    <label>Game Type:</label>
                    <div className="filter-controls">
                        <select
                            value={selectedGameType}
                            onChange={(e) =>
                                setSelectedGameType(e.target.value)
                            }
                        >
                            {GAME_TYPES.map((type) => (
                                <option key={type} value={type}>
                                    {type}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Opponent selector */}
                <div className="filter-group opponents-group">
                    <label>Opponents:</label>
                    <div className="filter-controls opponents-controls">
                        <div className="opponents-dropdown">
                            <div className="selected-opponents">
                                {selectedOpponents.length === 0 ? (
                                    <span className="no-opponents">
                                        Select opponents
                                    </span>
                                ) : (
                                    selectedOpponents.map((team) => (
                                        <span
                                            key={team}
                                            className="opponent-tag"
                                        >
                                            {team}
                                            <button
                                                type="button"
                                                className="remove-opponent"
                                                onClick={() =>
                                                    toggleOpponent(team)
                                                }
                                            >
                                                ×
                                            </button>
                                        </span>
                                    ))
                                )}
                            </div>
                            <div className="opponents-list">
                                {NBA_TEAMS.map((team) => (
                                    <div
                                        key={team}
                                        className={`opponent-option ${
                                            selectedOpponents.includes(team)
                                                ? 'selected'
                                                : ''
                                        }`}
                                        onClick={() => toggleOpponent(team)}
                                    >
                                        <input
                                            type="checkbox"
                                            checked={selectedOpponents.includes(
                                                team
                                            )}
                                            onChange={() => {}}
                                        />
                                        {team}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="filter-buttons">
                    <button
                        type="button"
                        className="filter-button apply-filter-button"
                        onClick={handleApplyFilters}
                    >
                        Apply Filters
                    </button>
                    <button
                        type="button"
                        className="filter-button clear-filter-button"
                        onClick={handleClearFilters}
                    >
                        Clear Filters
                    </button>
                </div>
            </div>
        </div>
    );
};

export default FilterSection;
