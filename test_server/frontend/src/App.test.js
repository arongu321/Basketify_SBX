import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';
import axios from 'axios';

// Mocking the axios GET request
jest.mock('axios');

describe('App', () => {
  // Test case for rendering the App and ensuring all elements are present
  test('renders main page with all required elements', async () => {
    // Mock the axios call to return favorites data
    axios.get.mockResolvedValueOnce({
      data: {
        player: 'LeBron James',
        team: 'Lakers',
      },
    });

    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    // Check if the loading screen shows initially
    expect(screen.getByText(/Loading.../)).toBeInTheDocument();

    // Wait for the favorites to load and page content to render
    await waitFor(() => {
      // Check for Basketify logo and title
      expect(screen.getByAltText(/Basketify Logo/)).toBeInTheDocument();
      expect(screen.getByText(/Basketify/)).toBeInTheDocument();

      // Check for logout link
      expect(screen.getByText(/Logout/)).toBeInTheDocument();

      // Check if favorite player and team are correctly displayed
      expect(screen.getByText(/Favourite Player: LeBron James/)).toBeInTheDocument();
      expect(screen.getByText(/Favourite Team: Lakers/)).toBeInTheDocument();
    });
  });

  // Test case for navigation button clicks (Search Player/Team, ML Predictions)
  test('navigates to the correct page when a tile is clicked', async () => {
    // Mock the axios call to return favorites data
    axios.get.mockResolvedValueOnce({
      data: {
        player: 'LeBron James',
        team: 'Lakers',
      },
    });

    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    // Wait for the content to load
    await waitFor(() => {
      // Check that the Search Player/Team tile is present
      const searchTile = screen.getByText('Search Player/Team');
      expect(searchTile).toBeInTheDocument();

      // Simulate a click on the "Search Player/Team" tile
      fireEvent.click(searchTile);

      // Check that the user is navigated to the /search page (use your routing to check)
      expect(window.location.pathname).toBe('/search');
    });

    // Test the "ML Predictions" tile navigation
    await waitFor(() => {
      const mlTile = screen.getByText('ML Predictions');
      expect(mlTile).toBeInTheDocument();
      fireEvent.click(mlTile);
      expect(window.location.pathname).toBe('/ml-predictions');
    });
  });

  // Test case for checking that the favorite player and team tiles work correctly (clickable)
  test('navigates to the correct player/team stats page when clicked', async () => {
    // Mock the axios call to return favorites data
    axios.get.mockResolvedValueOnce({
      data: {
        player: 'LeBron James',
        team: 'Lakers',
      },
    });

    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    // Wait for the content to load
    await waitFor(() => {
      // Check if the favorite player and team are clickable and navigate correctly
      const playerTile = screen.getByText('Favourite Player: LeBron James');
      const teamTile = screen.getByText('Favourite Team: Lakers');

      // Simulate clicks and check that the correct navigation happens
      fireEvent.click(playerTile);
      expect(window.location.pathname).toBe('/stats/player/LeBron James');

      fireEvent.click(teamTile);
      expect(window.location.pathname).toBe('/stats/team/Lakers');
    });
  });

  // Test case for checking the loading state when the favorites are being fetched
  test('shows loading screen when favorites are being fetched', () => {
    // Mock axios to return an empty data response or no favorites
    axios.get.mockResolvedValueOnce({
      data: {},
    });

    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    // The loading screen should be visible until the favorites load
    expect(screen.getByText(/Loading.../)).toBeInTheDocument();
  });
});
