import React, { useState } from 'react';
import '../styles/FilterSection.css';

const FilterSection = ({ isOpen, onApplyFilters }) => {
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');
    const [lastNGames, setLastNGames] = useState('');

    const handleApplyFilters = () => {
        // Construct query parameters for backend filtering
        const filters = {};

        if (dateFrom) filters.date_from = dateFrom;
        if (dateTo) filters.date_to = dateTo;
        if (lastNGames) filters.last_n_games = lastNGames;

        // Pass the filters to the parent component
        onApplyFilters(filters);
    };

    const handleClearFilters = () => {
        setDateFrom('');
        setDateTo('');
        setLastNGames('');

        // Clear filters in parent component with a flag to indicate it's a clear operation
        onApplyFilters({}, true);
    };

    if (!isOpen) return null;

    return (
        <div className="filter-section">
            <h3>Filter Options</h3>
            <div className="filter-content">
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
