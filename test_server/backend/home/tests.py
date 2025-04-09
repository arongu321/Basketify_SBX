from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .utils import apply_filters_to_games
import json


class ViewsTestCase(TestCase):
    # test the welcome message (used for debugging of React-Django connection)
    def test_welcome(self):
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, 'utf8'), {"message": "Welcome to Django with React!"})

    # test search for player, no name provided
    def test_search_player_no_name(self):
        response = self.client.get(reverse('search_player'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, 'utf8'), {'error': 'Name parameter is required'})

    # test search for a valid player (name present in mocked DB)
    @patch('home.views.get_mongo_client')
    def test_search_player_valid(self, mock_get_mongo_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_players_collection = MagicMock()

        mock_get_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_players_collection

        # mock return value of pymongo function call
        mock_players_collection.find.return_value = [
            {"name": "LeBron James", "team": "Lakers", "avg_ppg": 27.0},
            {"name": "LeBron Test", "team": "OKC", "avg_ppg": 21.9},
        ]

        # call the view we're testing with mocked DB behavior
        response = self.client.get(reverse('search_player') + '?name=LeBron')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("LeBron James", str(response.content, 'utf8'))

        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['players']), 2)  # two players returned
        self.assertEqual(response_data['players'][0]['name'], "LeBron James")

    # test search for player but no matching result in DB (no mocking required)
    def test_search_player_no_results(self):
        response = self.client.get(reverse('search_player') + '?name=NonExistentPlayer')
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(str(response.content, 'utf8'), {'message': 'No players found'})

    # test search for team, no name provided
    def test_search_team_no_name(self):
        response = self.client.get(reverse('search_team'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, 'utf8'), {'error': 'Name parameter is required'})

    # test search for a valid team (name present in mocked DB)
    @patch('home.views.get_mongo_client')
    def test_search_team_valid(self, mock_get_mongo_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_teams_collection = MagicMock()

        mock_get_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_teams_collection

        # mock return value of pymongo function call
        mock_teams_collection.find.return_value = [
            {"name": "Lakers", "location": "Los Angeles"}
        ]

        # call the view we're testing
        response = self.client.get(reverse('search_team') + '?name=Lakers')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Lakers", str(response.content, 'utf8'))

        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['teams']), 1) 
        self.assertEqual(response_data['teams'][0]['name'], "Lakers")

    # test search for team but no matching result in DB (no mocking required)
    def test_search_team_no_results(self):
        response = self.client.get(reverse('search_team') + '?name=NonExistentTeam')
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(str(response.content, 'utf8'), {'message': 'No teams found'})

    # test retrieving player stats but player name not in (mocked) DB
    @patch('home.views.get_mongo_client')
    def test_get_player_stats_player_not_found(self, mock_get_mongo_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_players_collection = MagicMock()

        mock_get_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_players_collection

        # mock the find_one pymongo function
        mock_players_collection.find_one.return_value = None

        response = self.client.get(reverse('player_stats', kwargs={'name': 'DoesNotExist'}))
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(str(response.content, 'utf8'), {'error': 'Player not found'})

    # test retrieving player stats and player name is present in (mocked) DB
    @patch('home.views.get_mongo_client')
    def test_get_player_stats_valid(self, mock_get_mongo_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_players_collection = MagicMock()

        mock_get_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_players_collection

        # in the view, the call to pymongo's find_one returns the dict below
        mock_players_collection.find_one.return_value = {"name": "LeBron James", "team": "Lakers", 
            'games': {'2025-04-06': {'Matchup': 'LAL @ OKC', 'Points': 19, 'scoredRebounds': 3, 
                                     'Assists': 7, 'FG_scored': 9, 'FG_pctg': 0.563, '3_pts_scored': 1, 
                                     '3_pts_pctg': 1.0, 'FT_made': 0, 'FT_pctg': 0, 'Steals': 1, 'Blocks': 0, 
                                     'Turnovers': 2, 'Team': 'LAL', 'WinLoss': 'W', 'is_future_game': False}}, 
            "future_games": {"2025-04-20": {"Matchup": "NYK @ BOS",
                                    "Points": 9, "scoredRebounds": 2, "Assists": 0, "FG_scored": 3, 
                                    "FG_pctg": 0.375, "3_pts_scored": 0, "3_pts_pctg": 0, "FT_made": 0, 
                                    "FT_pctg": 0, "Steals": 0, "Blocks": 2, "Turnovers": 1, "Team": "NYK", 
                                    "WinLoss": "W", "is_future_game":False}}}

        response = self.client.get(reverse('player_stats', kwargs={'name': 'LeBron James'}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("stats", response.json())
        self.assertIn("seasonal_stats", response.json())
        self.assertEqual(response.json()["stats"][0]["date"], "2025-04-06")
        self.assertEqual(response.json()["stats"][0]["points"], 19)
        self.assertEqual(response.json()["stats"][0]["fieldGoalsMade"], 9)

    # test retrieving team stats but team name not in (mocked) DB
    @patch('home.views.get_mongo_client')
    def test_get_team_stats_team_not_found(self, mock_get_mongo_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_teams_collection = MagicMock()

        mock_get_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_teams_collection

        # mock the pymongo find_one function to return None
        mock_teams_collection.find_one.return_value = None

        response = self.client.get(reverse('team_stats', kwargs={'name': 'NoTeam'}))
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(str(response.content, 'utf8'), {'error': 'Team not found'})

    # test retrieving team stats and team name is present in (mocked) DB
    @patch('home.views.get_mongo_client')
    def test_get_team_stats_valid(self, mock_get_mongo_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_teams_collection = MagicMock()

        mock_get_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_teams_collection

        # mock the find_one pymongo function to return this dict when called in the View
        mock_teams_collection.find_one.return_value = {"name": "Lakers", "abbrev_name": "LAL",
            'games': {'2025-04-02': {'Matchup': 'LAL @ OKC', 'Points': 84, 'scoredRebounds': 3, 
                                     'Assists': 7, 'FG_scored': 22, 'FG_pctg': 0.563, '3_pts_scored': 1, 
                                     '3_pts_pctg': 1.0, 'FT_made': 0, 'FT_pctg': 0, 'Steals': 1, 'Blocks': 0, 
                                     'Turnovers': 2, 'Team': 'LAL', 'WinLoss': 'W', 'is_future_game': False}}, 
            "future_games": {"2025-04-20": {"Matchup": "NYK @ BOS",
                                    "Points": 9, "scoredRebounds": 2, "Assists": 0, "FG_scored": 3, 
                                    "FG_pctg": 0.375, "3_pts_scored": 0, "3_pts_pctg": 0, "FT_made": 0, 
                                    "FT_pctg": 0, "Steals": 0, "Blocks": 2, "Turnovers": 1, "Team": "NYK", 
                                    "WinLoss": "W", "is_future_game":False}}}

        response = self.client.get(reverse('team_stats', kwargs={'name': 'Lakers'}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("stats", response.json())
        self.assertIn("seasonal_stats", response.json())
        self.assertEqual(response.json()["stats"][0]["date"], "2025-04-02")
        self.assertEqual(response.json()["stats"][0]["points"], 84)
        self.assertEqual(response.json()["stats"][0]["fieldGoalsMade"], 22)

    # test the predict nba champ View
    @patch('home.views.get_mongo_client')
    def test_predict_nba_champion(self, mock_get_mongo_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_teams_collection = MagicMock()

        mock_get_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_teams_collection

        # mock the find_one pymongo function to return this when called
        mock_teams_collection.find_one.return_value = {"name": "Lakers", "avg_ppg": 120.5}

        response = self.client.get(reverse('predict-season-champion'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["top_team"], "Lakers")
        self.assertEqual(data["top_team_ppg"], 120.5)

    # test the predict nba champ view but no data present
    @patch('home.views.get_mongo_client')
    def test_predict_nba_champion_no_data(self, mock_get_mongo_client):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_teams_collection = MagicMock()

        mock_get_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_teams_collection

        # mock find_one to return None
        mock_teams_collection.find_one.return_value = None

        response = self.client.get(reverse('predict-season-champion'))
        
        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(str(response.content, 'utf8'), {'error': "No team has avg_ppg recorded"})

class StatisticsFilteringTestCase(TestCase):
    """Tests for statistics filtering functionality (FR25-FR28)"""
    
    @patch('home.views.get_mongo_client')
    def setUp(self, mock_get_mongo_client):
        # Create mock database client
        self.client = Client()
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        
        mock_get_mongo_client.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection
        
        # Setup player data
        self.player_mock_data = {
            "name": "LeBron James",
            "games": {
                "2025-01-01": {
                    "Matchup": "LAL vs. BOS",
                    "Points": 30,
                    "scoredRebounds": 10,
                    "Assists": 8,
                    "Team": "LAL",
                    "WinLoss": "W",
                    "is_future_game": False
                },
                "2025-01-03": {
                    "Matchup": "LAL @ NYK",
                    "Points": 25,
                    "scoredRebounds": 8,
                    "Assists": 12,
                    "Team": "LAL",
                    "WinLoss": "L",
                    "is_future_game": False
                },
                "2025-01-05": {
                    "Matchup": "LAL vs. PHI",
                    "Points": 28,
                    "scoredRebounds": 7,
                    "Assists": 9,
                    "Team": "LAL",
                    "WinLoss": "W",
                    "is_future_game": False
                }
            }
        }
    
    # FR25 - Filter Criteria Display Tests
    @patch('home.views.get_mongo_client')
    def test_filter_params_are_processed(self, mock_get_mongo_client):
        """Test that filter parameters are correctly extracted from request"""
        # Setup mock response
        mock_get_mongo_client.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.mock_collection.find_one.return_value = self.player_mock_data
        
        # Query with filter parameters
        url = '/api/stats/player/LeBron James/?date_from=2025-01-02&date_to=2025-01-06&outcome=Win'
        response = self.client.get(url)
        
        # Check that function was called with correct filter parameters
        self.assertEqual(response.status_code, 200)
        # We'd ideally check that the filter function was called correctly, but would need a
        # more sophisticated mock setup. This is implicitly tested in the next tests.
    
    # FR26 + FR27 - Dynamic Update and Multiple Criteria Tests
    @patch('home.utils.apply_filters_to_games')
    @patch('home.views.get_mongo_client')
    def test_filter_apply_multiple_criteria(self, mock_get_mongo_client, mock_apply_filters):
        """Test that multiple filter criteria are applied correctly"""
        # Setup mocks
        mock_get_mongo_client.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.mock_collection.find_one.return_value = self.player_mock_data
        
        # Setup return value for apply_filters_to_games
        filtered_result = [
            {
                "date": "2025-01-05",
                "opponent": "PHI",
                "points": 28,
                "rebounds": 7,
                "assists": 9,
                "WinLoss": "W"
            }
        ]
        mock_apply_filters.return_value = filtered_result
        
        # Prepare filter parameters
        filters = {
            'date_from': '2025-01-04',
            'outcome': 'Win',
            'opponents': 'PHI'
        }
        
        # Construct URL with query parameters
        query_string = '&'.join([f'{key}={value}' for key, value in filters.items()])
        url = f'/api/stats/player/LeBron James/?{query_string}'
        
        # Perform the request
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, 200, f"Unexpected response status: {response.content}")
        
        
        # Check response content
        data = json.loads(response.content)
        self.assertIn('stats', data, "Response should contain 'stats' key")
        self.assertEqual(len(data['stats']), 1, "Expected one filtered result")
        
        # Verify specific details of the filtered result
        filtered_game = data['stats'][0]
        self.assertEqual(filtered_game['date'], '2025-01-05', "Unexpected filtered game date")
        self.assertEqual(filtered_game['opponent'], 'PHI', "Unexpected filtered game opponent")
        self.assertEqual(filtered_game['points'], 28, "Unexpected filtered game points")
    
    # FR28 - Filter Reset Test
    @patch('home.utils.apply_filters_to_games')
    @patch('home.views.get_mongo_client')
    def test_filter_reset(self, mock_get_mongo_client, mock_apply_filters):
        """Test that filter reset returns all data (no filters applied)"""
        # Setup mocks
        mock_get_mongo_client.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.mock_collection.find_one.return_value = self.player_mock_data
        
        # Setup mock return for all data (no filters)
        all_games = [
            {
                "date": "2025-01-01",
                "opponent": "BOS",
                "points": 30,
                "rebounds": 10,
                "assists": 8,
                "WinLoss": "W"
                # Other stats would be here
            },
            {
                "date": "2025-01-03",
                "opponent": "NYK",
                "points": 25,
                "rebounds": 8,
                "assists": 12,
                "WinLoss": "L"
                # Other stats would be here
            },
            {
                "date": "2025-01-05",
                "opponent": "PHI",
                "points": 28,
                "rebounds": 7,
                "assists": 9,
                "WinLoss": "W"
                # Other stats would be here
            }
        ]
        mock_apply_filters.return_value = all_games
        
        # Make request with no filters
        response = self.client.get('/api/stats/player/LeBron James/')
        
        # Check response contains all data
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['stats']), 3)
    
    # Additional filter-specific tests
    @patch('home.utils.apply_filters_to_games')
    @patch('home.views.get_mongo_client')
    def test_date_range_filter(self, mock_get_mongo_client, mock_apply_filters):
        """Test that date range filter correctly limits results by date"""
        # Setup mocks similar to previous tests
        mock_get_mongo_client.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.mock_collection.find_one.return_value = self.player_mock_data
        
        # Setup filtered data mock return
        filtered_data = [
            {
                "date": "2025-01-03",
                "opponent": "NYK",
                "points": 25,
                "rebounds": 8,
                "assists": 12,
                "WinLoss": "L"
                # Other stats would be here
            }
        ]
        mock_apply_filters.return_value = filtered_data
        
        # Query with date range filter
        url = '/api/stats/player/LeBron James/?date_from=2025-01-02&date_to=2025-01-04'
        response = self.client.get(url)
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['stats']), 1)
        self.assertEqual(data['stats'][0]['date'], '2025-01-03')
    
    @patch('home.utils.apply_filters_to_games')
    @patch('home.views.get_mongo_client')
    def test_opponent_filter(self, mock_get_mongo_client, mock_apply_filters):
        """Test that opponent filter correctly filters by opponent team"""
        # Setup mocks
        mock_get_mongo_client.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.mock_collection.find_one.return_value = self.player_mock_data
        
        # Setup filtered data mock return
        filtered_data = [
            {
                "date": "2025-01-01",
                "opponent": "BOS",
                "points": 30,
                "rebounds": 10,
                "assists": 8,
                "WinLoss": "W"
                # Other stats would be here
            }
        ]
        mock_apply_filters.return_value = filtered_data
        
        # Query with opponent filter
        url = '/api/stats/player/LeBron James/?opponents=Boston Celtics'
        response = self.client.get(url)
        
        # Validate response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['stats']), 1)
        self.assertEqual(data['stats'][0]['opponent'], 'BOS')
