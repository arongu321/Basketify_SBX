import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SearchInterface from '../components/SearchInterface';
import api from '../utils/api'; // Mocked api
import '@testing-library/jest-dom';
import { BrowserRouter as Router, useNavigate, useLocation, MemoryRouter, Routes, Route } from 'react-router-dom';

// Mock the necessary functions
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
  useLocation: jest.fn(),
}));

jest.mock('../utils/api'); // Mock the API calls

describe('SearchInterface Component', () => {
  let mockNavigate;
  beforeEach(() => {
    mockNavigate = jest.fn();
    useNavigate.mockReturnValue(mockNavigate); // Mock navigate function
    useLocation.mockReturnValue({
      state: {}, // Test case for player
    });
  });

  test('should render correctly with initial search state', () => {
    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    // Check if input and buttons are rendered
    expect(screen.getByPlaceholderText(/Enter player name/i)).toBeInTheDocument();
    expect(screen.getAllByText('Search Players')).toHaveLength(2);
  });

  test('should handle search term input', () => {
    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });

    expect(searchInput.value).toBe('LeBron');
  });

  test('should display loading indicator while fetching results', async () => {
    api.get.mockResolvedValueOnce([{name: "LeBron"}]);
    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });
    fireEvent.click(screen.getByText('Search'));

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('should show search results when API call succeeds for player', async () => {
    // Mocking successful API response
    api.get.mockResolvedValueOnce({
      data: { players: [{ name: 'LeBron James' }] },
    });

    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });
    fireEvent.click(screen.getByText('Search'));

    await waitFor(() => {
      expect(screen.getByText('LeBron James')).toBeInTheDocument();
    });
  });

  test('should display "no results found" when no players are found', async () => {
    // Mocking API response with no players found
    api.get.mockResolvedValueOnce({
      data: { players: [] },
    });

    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'Unknown Player' } });
    fireEvent.click(screen.getByText('Search'));

    await waitFor(() => {
      expect(screen.getByText('No results found for "Unknown Player".')).toBeInTheDocument();
    });
  });

  test('should toggle between player and team search when setFavorite is not set', async () => {
    render(
        <Router>
          <SearchInterface />
        </Router>
    );

    // Check both "Search Players" and "Search Teams" buttons are rendered
    expect(screen.getAllByText('Search Players')).toHaveLength(2);
    expect(screen.getByText('Search Teams')).toBeInTheDocument();

    // Click to switch to team search
    fireEvent.click(screen.getByText('Search Teams'));
    await waitFor(() => {
        // Title should now reflect "Search Teams"
        expect(screen.getAllByText('Search Teams')[0]).toHaveClass('search-interface-title');
    });

    // Click back to player
    fireEvent.click(screen.getByText('Search Players'));
    await waitFor(() => {
        expect(screen.getAllByText('Search Players')[0]).toHaveClass('search-interface-title');
    });
  });

  test('should navigate to stats page when a result is clicked', async () => {
    // Mocking successful API response for GET
    api.get.mockResolvedValueOnce({
      data: { players: [{ name: 'LeBron James' }] },
    });
  
    api.post.mockResolvedValueOnce({}); // Even if unused, avoid breaking
  
    render(
      <Router>
        <SearchInterface />
      </Router>
    );
  
    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });
    fireEvent.click(screen.getByText('Search'));
  
    await waitFor(() => {
      // Click result
      fireEvent.click(screen.getByText('LeBron James'));
  
      // Assert navigate call
      expect(mockNavigate).toHaveBeenCalledWith('/stats/player/LeBron James');
    });
  });
  

  test('should save favorite player when clicked', async () => {
    useLocation.mockReturnValue({
        state: { setFavorite: 'player' }, // Test case for player
    });

    // Mocking successful API response for GET request
    api.get.mockResolvedValueOnce({
      data: { players: [{ name: 'LeBron James' }] },
    });
  
    // Mocking the POST request to save the favorite player
    api.post.mockResolvedValueOnce({});  // Mock successful response for post request
  
    render(
      <Router>
        <SearchInterface />
      </Router>
    );
  
    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });
    fireEvent.click(screen.getByText('Search'));
  
    await waitFor(() => expect(screen.getByText('LeBron James', {exact: false})).toBeInTheDocument());
  
    // Trigger click event on the result item
    fireEvent.click(screen.getByText('LeBron James'));

    // Ensure the post API call is made to save the favorite player
    expect(api.post).toHaveBeenCalledWith(
    '/accounts/set-favorite/',
    {
        type: 'player',
        name: 'LeBron James',
    },
    expect.anything()
    );
  });
  

  test('should handle error when saving favorite', async () => {
    useLocation.mockReturnValue({
        state: { setFavorite: 'player' }, // Test case for player
    });

    // Mocking successful API response
    api.get.mockResolvedValueOnce({
      data: { players: [{ name: 'LeBron James' }] },
    });

    // Mocking the post request for saving the favorite to fail
    api.post.mockRejectedValueOnce(new Error('Failed to save favorite'));

    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });
    fireEvent.click(screen.getByText('Search'));

    await waitFor(() => {
      fireEvent.click(screen.getByText('LeBron James'));
      expect(api.post).toHaveBeenCalledWith(
        '/accounts/set-favorite/',
        {
          type: 'player',
          name: 'LeBron James',
        },
        expect.anything()
      );
    });
  });
});
