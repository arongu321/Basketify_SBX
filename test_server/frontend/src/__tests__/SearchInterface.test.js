import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SearchInterface from '../components/SearchInterface';
import api from '../utils/api';  // actually uses the __mock__/api.js file
import '@testing-library/jest-dom';
import { BrowserRouter as Router, useNavigate, useLocation } from 'react-router-dom';

// mock the useNavigate and useLocation functions so we can catch the calls to
// these functions (rather than actually executing them)
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
  useLocation: jest.fn(),
}));

jest.mock('../utils/api');  // necessary to prevent error on "import.meta" in utils/api.js

describe('SearchInterface Component', () => {
  let mockNavigate;
  beforeEach(() => {
    mockNavigate = jest.fn();
    useNavigate.mockReturnValue(mockNavigate);
    useLocation.mockReturnValue({
      state: {},  // enter the search page on search mode (not favourite player/team select mode) by default, overriden in favourite test case functions
    });
  });

  // test rendering of the search page
  test('render_search_page', () => {
    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    // verify input form is displayed and search players is default
    expect(screen.getByPlaceholderText(/Enter player name/i)).toBeInTheDocument();
    expect(screen.getAllByText('Search Players')).toHaveLength(2);
  });

  // test search input form takes user input as expected
  test('search_input', () => {
    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    // put text into search bar
    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });

    // make sure search term is recorded and visible
    expect(searchInput.value).toBe('LeBron');
  });

  // test loading screen displayed
  test('search_loading_screen', async () => {
    api.get.mockResolvedValueOnce([{name: "LeBron"}]);
    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    // put in search term and hit search button
    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });
    fireEvent.click(screen.getByText('Search'));

    // verify loading is present
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  // test search for player returns values expected
  test('search_player', async () => {
    // mock the Django GET request to return LeBron James
    api.get.mockResolvedValueOnce({
      data: { players: [{ name: 'LeBron James' }] },
    });

    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    // trigger user input
    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });
    fireEvent.click(screen.getByText('Search'));

    // verify value returned by Django is printed
    await waitFor(() => {
      expect(screen.getByText('LeBron James')).toBeInTheDocument();
    });
  });

  // test display for no results is handled by "no results" message
  test('search_player_no_results', async () => {
    // mock Django GET request to return nothing
    api.get.mockResolvedValueOnce({
      data: { players: [] },
    });

    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    // trigger user input
    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'Unknown Player' } });
    fireEvent.click(screen.getByText('Search'));

    // verify "no results" message displayed
    await waitFor(() => {
      expect(screen.getByText('No results found for "Unknown Player".')).toBeInTheDocument();
    });
  });

  // test the toggle between player and team search mode
  test('search_toggle_player_team', async () => {
    render(
        <Router>
          <SearchInterface />
        </Router>
    );

    // check both "Search Players" and "Search Teams" buttons are rendered
    expect(screen.getAllByText('Search Players')).toHaveLength(2);  // appears twice (button + text)
    expect(screen.getByText('Search Teams')).toBeInTheDocument();

    // switch to team search
    fireEvent.click(screen.getByText('Search Teams'));
    await waitFor(() => {
        // verify title should be "Search Teams"
        expect(screen.getAllByText('Search Teams')[0]).toHaveClass('search-interface-title');
    });

    // switch to player search
    fireEvent.click(screen.getByText('Search Players'));
    await waitFor(() => {
        // verify title should be "Search Players"
        expect(screen.getAllByText('Search Players')[0]).toHaveClass('search-interface-title');
    });
  });

  // test that clicking on a player name in results list takes user to stats page
  test('search_to_stats_navigation_player', async () => {
    // mock Django GET Requets to return LeBron
    api.get.mockResolvedValueOnce({
      data: { players: [{ name: 'LeBron James' }] },
    });
  
    api.post.mockResolvedValueOnce({}); // only used by set favourite, left so test won't break if incorrectly designed
  
    render(
      <Router>
        <SearchInterface />
      </Router>
    );
  
    // trigger user search for lebron
    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });
    fireEvent.click(screen.getByText('Search'));
  
    await waitFor(() => {
      // click on lebron's name
      fireEvent.click(screen.getByText('LeBron James'));
  
      // assert we called useNavigate to the path
      expect(mockNavigate).toHaveBeenCalledWith('/stats/player/LeBron James');
    });
  });
  
  // tests setting of favourite player
  test('set_favourite_player', async () => {
    useLocation.mockReturnValue({
        state: { setFavorite: 'player' }, // we render the page in a different way when setting favourite, using the state attr
    });

    // mock the search GET requests return from Django
    api.get.mockResolvedValueOnce({
      data: { players: [{ name: 'LeBron James' }] },
    });
  
    // mock the POST request so we can assert correct request was sent
    api.post.mockResolvedValueOnce({});  // mock POST doesn't do anything
  
    render(
      <Router>
        <SearchInterface />
      </Router>
    );
  
    // trigger user search for Lebron
    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });
    fireEvent.click(screen.getByText('Search'));
  
    // wait until search results rendered
    await waitFor(() => expect(screen.getByText('LeBron James', {exact: false})).toBeInTheDocument());
  
    // trigger click on lebron's name
    fireEvent.click(screen.getByText('LeBron James'));

    // verify POST request sent to /accounts/set-favorite/ with correct type and name fields
    expect(api.post).toHaveBeenCalledWith(
    '/accounts/set-favorite/',
    {
        type: 'player',
        name: 'LeBron James',
    },
    expect.anything()
    );
  });
  
  // test graceful handling of failed set favourite
  test('set_favourite_player_error', async () => {
    useLocation.mockReturnValue({
        state: { setFavorite: 'player' },  // we render the page in a different way when setting favourite, using the state attr
    });

    // mock the Django GET request to return Lebron
    api.get.mockResolvedValueOnce({
      data: { players: [{ name: 'LeBron James' }] },
    });

    // mock the POST request to return an error on Django's side
    api.post.mockRejectedValueOnce(new Error('Failed to save favorite'));

    render(
      <Router>
        <SearchInterface />
      </Router>
    );

    // trigger user input to search for lebron
    const searchInput = screen.getByPlaceholderText('Enter player name');
    fireEvent.change(searchInput, { target: { value: 'LeBron' } });
    fireEvent.click(screen.getByText('Search'));

    await waitFor(() => {
      fireEvent.click(screen.getByText('LeBron James'));  // trigger click on lebron's name
      // verify POST request sent with correct fields
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
