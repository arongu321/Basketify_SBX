import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import MLPredictions from '../components/MLPredictions';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('MLPredictions Component', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('displays loading state initially', () => {
    // 👇 Provide a dummy pending promise to prevent .then error
    axios.get.mockImplementationOnce(() => new Promise(() => {}));

    render(
      <MemoryRouter>
        <MLPredictions />
      </MemoryRouter>
    );

    expect(screen.getByText('Loading Predictions...')).toBeInTheDocument();
    expect(screen.getByAltText('Loading...')).toBeInTheDocument();
  });

  test('displays predicted team and PPG after data is fetched', async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        top_team: 'Golden State Warriors',
        top_team_ppg: 118.3,
      },
    });

    render(
      <MemoryRouter>
        <MLPredictions />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Predicted NBA Champion: Golden State Warriors')).toBeInTheDocument();
      expect(screen.getByText('Average predicted points per game: 118.3')).toBeInTheDocument();
    });
  });

  test('handles API error gracefully and exits loading state', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {}); // silence error in output
  
    axios.get.mockRejectedValueOnce(new Error('API error'));
  
    render(
      <MemoryRouter>
        <MLPredictions />
      </MemoryRouter>
    );
  
    await waitFor(() => {
      expect(screen.queryByText('Loading Predictions...')).not.toBeInTheDocument();
    });
  
    // Check that the error was logged
    expect(consoleSpy).toHaveBeenCalledWith(
      'There was an error fetching the predicted NBA champion:',
      expect.any(Error)
    );
  
    consoleSpy.mockRestore(); // clean up
  });
  

  test('back button exists and triggers navigation', async () => {
    // We want to wait for it to load, so we provide a valid mock
    axios.get.mockResolvedValueOnce({
      data: {
        top_team: 'Boston Celtics',
        top_team_ppg: 117.1,
      },
    });

    render(
      <MemoryRouter>
        <MLPredictions />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Predicted NBA Champion: Boston Celtics')).toBeInTheDocument();
    });

    const backButton = screen.getByText('Back');
    fireEvent.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });
});
