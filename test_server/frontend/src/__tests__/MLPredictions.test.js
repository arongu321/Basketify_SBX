import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import MLPredictions from '../components/MLPredictions';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';

// mock axios for GET requests
jest.mock('axios');

// mock useNavigate so we can catch requests for back button clicks
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

  test('ml_pred_loading', () => {
    // mock axios GET request so we can catch and inspect the request
    axios.get.mockImplementationOnce(() => new Promise(() => {}));

    render(
      <MemoryRouter>
        <MLPredictions />
      </MemoryRouter>
    );

    // verify loading screen is displayed
    expect(screen.getByText('Loading Predictions...')).toBeInTheDocument();
    expect(screen.getByAltText('Loading...')).toBeInTheDocument();
  });

  // test NBA champion and ppg displayed
  test('ml_pred_prediction', async () => {
    // mock axios GET request to return this data (testing of Django done in backend/ folder)
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

    // verify NBA champion and ppg displayed as expected
    await waitFor(() => {
      expect(screen.getByText('Predicted NBA Champion: Golden State Warriors')).toBeInTheDocument();
      expect(screen.getByText('Average predicted points per game: 118.3')).toBeInTheDocument();
    });
  });

  // test errors from Django are handled gracefully
  test('ml_pred_error', async () => {
    // mock console log to catch the error message
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  
    // mock axios GET request to return an error
    axios.get.mockRejectedValueOnce(new Error('API error'));
  
    render(
      <MemoryRouter>
        <MLPredictions />
      </MemoryRouter>
    );
  
    // wait until done loading
    await waitFor(() => {
      expect(screen.queryByText('Loading Predictions...')).not.toBeInTheDocument();
    });
  
    // verify the error was logged in console
    expect(consoleSpy).toHaveBeenCalledWith(
      'There was an error fetching the predicted NBA champion:',
      expect.any(Error)
    );
  
    consoleSpy.mockRestore(); // clean up
  });
  
  // test the back button triggers navigation to home page
  test('ml_pred_back_button', async () => {
    // mock axios GET request
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

    // wait until done loading
    await waitFor(() => {
      expect(screen.getByText('Predicted NBA Champion: Boston Celtics')).toBeInTheDocument();
    });

    // trigger user click on back button
    const backButton = screen.getByText('Back');
    fireEvent.click(backButton);

    // verify navigation to home page initiated
    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });
});
