import React, { useState, useEffect } from 'react';
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

// FR25, FR26, FR27, FR28 - This component handles the filter UI for statistics
/**
 * @typedef {Object} Filters
 * @property {string} [date_from] - Start date for the date range filter.
 * @property {string} [date_to] - End date for the date range filter.
 * @property {string} [last_n_games] - Number of last games to filter by.
 * @property {string} [season] - Season to filter by.
 * @property {string} [season_type] - Type of season to filter by (e.g., Regular Season, Playoffs).
 * @property {string} [division] - Division to filter by.
 * @property {string} [conference] - Conference to filter by.
 * @property {string} [game_type] - Type of game to filter by.
 * @property {string} [outcome] - Outcome of the game to filter by.
 * @property {string} [opponents] - Comma-separated string of opponent teams to filter by.
 */

/**
 * FilterSection Component - Handles the filter UI for statistics. Allows users to apply various filters such as date ranges, seasons,
 * season types, divisions, conferences, game types, game outcomes, and opponents.
 *
 * @param {Object} props - Component props.
 * @param {boolean} props.isOpen - Determines if the filter section is open or closed.
 * @param {function(Filters): void} props.onApplyFilters - Callback function to apply the selected filters.
 * @param {string} props.entityType - The type of entity being filtered (e.g., 'team', 'player').  This determines available seasons.
 * @param {Filters} props.initialFilters - Initial filter values to populate the filter section with.
 * @returns {JSX.Element|null} - Returns the JSX structure for the filter section, or null if the filter is not open.
 */
const FilterSection = ({
    isOpen,
    onApplyFilters,
    entityType,
    initialFilters = {}, // New prop to receive initial filter state
}) => {
    // FR25 - Initialize state with initial filters or empty values
    const [dateFrom, setDateFrom] = useState(initialFilters.date_from || '');
    const [dateTo, setDateTo] = useState(initialFilters.date_to || '');
    const [lastNGames, setLastNGames] = useState(
        initialFilters.last_n_games || ''
    );

    const [selectedSeason, setSelectedSeason] = useState(
        initialFilters.season || ''
    );
    const [selectedSeasonType, setSelectedSeasonType] = useState(
        initialFilters.season_type || ''
    );
    const [selectedDivision, setSelectedDivision] = useState(
        initialFilters.division || ''
    );
    const [selectedConference, setSelectedConference] = useState(
        initialFilters.conference || ''
    );
    const [selectedGameType, setSelectedGameType] = useState(
        initialFilters.game_type || ''
    );
    const [selectedOutcome, setSelectedOutcome] = useState(
        initialFilters.outcome || ''
    );
    const [selectedOpponents, setSelectedOpponents] = useState(
        initialFilters.opponents ? initialFilters.opponents.split(',') : []
    );

    // FR28 - Reset filters to the initial state
    const handleClearFilters = () => {
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
    };

    // FR26, FR27 - Apply filters when user clicks apply button
    const handleApplyFilters = () => {
        const filters = {};

        // FR27 - Build filter object with all selected filter criteria
        // Date range filters
        if (dateFrom) filters.date_from = dateFrom;
        if (dateTo) filters.date_to = dateTo;
        if (lastNGames) filters.last_n_games = lastNGames;

        // Additional filters
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

        // FR26 - Pass the filters to the parent component for API call
        onApplyFilters(filters);
    };

    // FR25 - This is part of the multiple opponents selection UI for filtering
    const toggleOpponent = (team) => {
        setSelectedOpponents((prev) =>
            prev.includes(team)
                ? prev.filter((t) => t !== team)
                : [...prev, team]
        );
    };

    // FR25 - Don't show filter UI when closed
    if (!isOpen) return null;

    return (
        <div className="filter-section">
            <h3>Filter Options</h3>
            <div className="filter-content">
                {/* All existing filter inputs remain the same */}
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
                            {NBA_SEASONS[entityType].map((season) => (
                                <option key={season} value={season}>
                                    {season}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Remaining filter groups remain unchanged */}
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

                {/* Conference type filter */}
                <div className="filter-group">
                    <label>Conference Type:</label>
                    <div className="filter-controls">
                        <select
                            value={selectedGameType}
                            onChange={(e) =>
                                setSelectedGameType(e.target.value)
                            }
                        >
                            <option value="">All Conference Types</option>
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
