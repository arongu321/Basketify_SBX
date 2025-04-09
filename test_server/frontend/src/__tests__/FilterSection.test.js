import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FilterSection from '../components/FilterSection';
import '@testing-library/jest-dom';

describe('Filter Section Tests (FR25-FR28)', () => {
    const mockApplyFilters = jest.fn();

    afterEach(() => {
        jest.clearAllMocks();
    });

    // Helper function to render the component
    const renderFilterSection = (isOpen = true, initialFilters = {}) => {
        return render(
            <FilterSection
                isOpen={isOpen}
                onApplyFilters={mockApplyFilters}
                entityType="player"
                initialFilters={initialFilters}
            />
        );
    };

    // FR25 - Filter Criteria Display Tests
    describe('FR25 - Filter Criteria Display', () => {
        test('filter_section_not_visible_when_closed', () => {
            renderFilterSection(false);
            expect(
                screen.queryByText('Filter Options')
            ).not.toBeInTheDocument();
        });

        test('filter_section_visible_when_open', () => {
            renderFilterSection(true);
            expect(screen.getByText('Filter Options')).toBeInTheDocument();
        });

        test('filter_displays_all_criteria_options', () => {
            renderFilterSection();

            // Verify all filter categories are displayed
            expect(screen.getByText('Date Range:')).toBeInTheDocument();
            expect(screen.getByText('Season:')).toBeInTheDocument();
            expect(screen.getByText('Season Type:')).toBeInTheDocument();
            expect(screen.getByText('Game Outcome:')).toBeInTheDocument();
            expect(screen.getByText('Last N Games:')).toBeInTheDocument();
            expect(screen.getByText('Conference:')).toBeInTheDocument();
            expect(screen.getByText('Division:')).toBeInTheDocument();
            expect(screen.getByText('Conference Type:')).toBeInTheDocument();
            expect(screen.getByText('Opponents:')).toBeInTheDocument();

            // Verify buttons
            expect(
                screen.getByRole('button', { name: /Apply Filters/i })
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: /Clear Filters/i })
            ).toBeInTheDocument();
        });
    });

    // FR26 - Dynamic Update Tests
    describe('FR26 - Dynamic Update', () => {
        test('filter_date_range_update', async () => {
            renderFilterSection();

            // Get date inputs
            const dateFromInput = screen.getByPlaceholderText('Start Date');
            const dateToInput = screen.getByPlaceholderText('End Date');

            // Change date values
            fireEvent.change(dateFromInput, {
                target: { value: '2025-01-01' },
            });
            fireEvent.change(dateToInput, { target: { value: '2025-12-31' } });

            // Apply filters
            fireEvent.click(
                screen.getByRole('button', { name: /Apply Filters/i })
            );

            // Check if callback was called with correct filter values
            expect(mockApplyFilters).toHaveBeenCalledWith(
                expect.objectContaining({
                    date_from: '2025-01-01',
                    date_to: '2025-12-31',
                })
            );
        });

        test('filter_last_n_games_update', async () => {
            renderFilterSection();

            // Get last N games input
            const lastNGamesInput = screen.getByPlaceholderText(
                'Enter number of games'
            );

            // Change value
            fireEvent.change(lastNGamesInput, { target: { value: '10' } });

            // Apply filters
            fireEvent.click(
                screen.getByRole('button', { name: /Apply Filters/i })
            );

            // Check if callback was called with correct filter values
            expect(mockApplyFilters).toHaveBeenCalledWith(
                expect.objectContaining({
                    last_n_games: '10',
                })
            );
        });

        test('filter_season_update', async () => {
            const { container } = renderFilterSection();

            // Get all select elements and find the one following the Season: label
            const seasonLabel = screen.getByText('Season:');
            const seasonSelectWrapper = seasonLabel.closest('.filter-group');
            const seasonSelect = seasonSelectWrapper.querySelector('select');

            // Change value to first season in dropdown (after "All Seasons")
            fireEvent.change(seasonSelect, { target: { value: '2022-23' } });

            // Apply filters
            fireEvent.click(
                screen.getByRole('button', { name: /Apply Filters/i })
            );

            // Check if callback was called with correct filter values
            expect(mockApplyFilters).toHaveBeenCalledWith(
                expect.objectContaining({
                    season: '2022-23',
                })
            );
        });
    });

    // FR27 - Multiple Filter Criteria Tests
    describe('FR27 - Multiple Filter Criteria', () => {
        test('apply_multiple_filters_simultaneously', async () => {
            const { container } = renderFilterSection();

            // Set multiple filter values
            fireEvent.change(screen.getByPlaceholderText('Start Date'), {
                target: { value: '2025-01-01' },
            });
            fireEvent.change(
                screen.getByPlaceholderText('Enter number of games'),
                { target: { value: '5' } }
            );

            // Select a specific season type
            const seasonTypeLabel = screen.getByText('Season Type:');
            const seasonTypeWrapper = seasonTypeLabel.closest('.filter-group');
            const seasonTypeSelect = seasonTypeWrapper.querySelector('select');

            fireEvent.change(seasonTypeSelect, {
                target: { value: 'Regular Season' },
            });

            // Select a specific game outcome
            const outcomeLabel = screen.getByText('Game Outcome:');
            const outcomeWrapper = outcomeLabel.closest('.filter-group');
            const outcomeSelect = outcomeWrapper.querySelector('select');

            fireEvent.change(outcomeSelect, { target: { value: 'Win' } });

            // Apply filters
            fireEvent.click(
                screen.getByRole('button', { name: /Apply Filters/i })
            );

            // Check if callback was called with all filter values
            expect(mockApplyFilters).toHaveBeenCalledWith({
                date_from: '2025-01-01',
                last_n_games: '5',
                season_type: 'Regular Season',
                outcome: 'Win',
            });
        });

        test('opponents_filter_multiple_selection', async () => {
            const { container } = renderFilterSection();

            // Open opponents dropdown to view options
            const opponentsDropdown = screen.getByText('Select opponents');
            fireEvent.click(opponentsDropdown);

            // Find the opponent options in the dropdown
            const opponentsList = container.querySelector('.opponents-list');

            // Find specific team options
            const bostonOption = Array.from(
                opponentsList.querySelectorAll('.opponent-option')
            ).find((option) => option.textContent.includes('Boston Celtics'));
            const lakersOption = Array.from(
                opponentsList.querySelectorAll('.opponent-option')
            ).find((option) =>
                option.textContent.includes('Los Angeles Lakers')
            );

            // Click on the team options
            if (bostonOption) fireEvent.click(bostonOption);
            if (lakersOption) fireEvent.click(lakersOption);

            // Apply filters
            fireEvent.click(
                screen.getByRole('button', { name: /Apply Filters/i })
            );

            // Check if callback was called with correct opponents
            expect(mockApplyFilters).toHaveBeenCalledWith(
                expect.objectContaining({
                    opponents: 'Boston Celtics,Los Angeles Lakers',
                })
            );
        });
    });

    // FR28 - Filter Reset Tests
    describe('FR28 - Filter Reset', () => {
        test('clear_filters_button_resets_all_filters', async () => {
            // Initialize with some filters
            const initialFilters = {
                date_from: '2025-01-01',
                date_to: '2025-12-31',
                last_n_games: '10',
                season: '2024-25',
                outcome: 'Win',
            };

            renderFilterSection(true, initialFilters);

            // Verify initial filters are set
            expect(screen.getByPlaceholderText('Start Date').value).toBe(
                '2025-01-01'
            );
            expect(screen.getByPlaceholderText('End Date').value).toBe(
                '2025-12-31'
            );
            expect(
                screen.getByPlaceholderText('Enter number of games').value
            ).toBe('10');

            // Clear filters
            fireEvent.click(
                screen.getByRole('button', { name: /Clear Filters/i })
            );

            // Verify fields are cleared
            expect(screen.getByPlaceholderText('Start Date').value).toBe('');
            expect(screen.getByPlaceholderText('End Date').value).toBe('');
            expect(
                screen.getByPlaceholderText('Enter number of games').value
            ).toBe('');

            // Apply empty filters
            fireEvent.click(
                screen.getByRole('button', { name: /Apply Filters/i })
            );

            // Check if callback was called with empty object
            expect(mockApplyFilters).toHaveBeenCalledWith({});
        });

        test('initialize_with_existing_filters', async () => {
            // Initialize with some filters
            const initialFilters = {
                date_from: '2025-01-01',
                date_to: '2025-12-31',
                last_n_games: '10',
                season: '2024-25',
                outcome: 'Win',
                opponents: 'Boston Celtics,Los Angeles Lakers',
            };

            renderFilterSection(true, initialFilters);

            // Verify initial filters are set
            expect(screen.getByPlaceholderText('Start Date').value).toBe(
                '2025-01-01'
            );
            expect(screen.getByPlaceholderText('End Date').value).toBe(
                '2025-12-31'
            );
            expect(
                screen.getByPlaceholderText('Enter number of games').value
            ).toBe('10');

            // We can't easily test the select values directly, but we can verify they're passed correctly
            // when applying filters without changes

            // Apply filters without changes
            fireEvent.click(
                screen.getByRole('button', { name: /Apply Filters/i })
            );

            // Check if callback was called with same filters
            expect(mockApplyFilters).toHaveBeenCalledWith(initialFilters);
        });
    });

    // Additional Integration Tests
    describe('Filter Integration Tests', () => {
        test('removing_opponent_from_selection', async () => {
            // Initialize with opponents
            const initialFilters = {
                opponents: 'Boston Celtics,Los Angeles Lakers',
            };

            const { container } = renderFilterSection(true, initialFilters);

            // Get the selected-opponents area
            const selectedOpponentsArea = container.querySelector(
                '.selected-opponents'
            );

            // Verify the selected opponents are present
            expect(selectedOpponentsArea.textContent).toContain(
                'Boston Celtics'
            );
            expect(selectedOpponentsArea.textContent).toContain(
                'Los Angeles Lakers'
            );

            // Find remove buttons
            const removeButtons =
                container.querySelectorAll('.remove-opponent');
            expect(removeButtons.length).toBe(2);

            // Click the first remove button (Boston Celtics)
            fireEvent.click(removeButtons[0]);

            // Apply filters
            fireEvent.click(screen.getByText('Apply Filters'));

            // Check if mockApplyFilters was called with only Los Angeles Lakers
            expect(mockApplyFilters).toHaveBeenCalledWith(
                expect.objectContaining({
                    opponents: 'Los Angeles Lakers',
                })
            );
        });
    });
});
