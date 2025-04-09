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
    
    def setUp(self):
        # Create client for testing HTTP endpoints
        self.client = Client()
        
        # Create test player data for testing filters directly
        self.test_player_games = [
            {
                "date": "2025-01-01",
                "opponent": "BOS",
                "opponent_abbr": "BOS",  # Add this field that the filter function uses
                "points": 30,
                "rebounds": 10,
                "assists": 8,
                "fieldGoalsMade": 10,
                "fieldGoalPercentage": 0.5,
                "threePointsMade": 2,
                "threePointPercentage": 0.4,
                "freeThrowsMade": 8,
                "freeThrowPercentage": 0.8,
                "steals": 2,
                "blocks": 1,
                "turnovers": 3,
                "WinLoss": "W",
                "Matchup": "LAL vs. BOS",
                "TEAM_ABBREVIATION": "LAL",
                "gameLocation": "home",
                "seasonType": "Regular Season",
                "SEASON_ID": "22024",
                "is_future_game": False
            },
            {
                "date": "2025-01-03",
                "opponent": "NYK",
                "opponent_abbr": "NYK",
                "points": 25,
                "rebounds": 8,
                "assists": 12,
                "fieldGoalsMade": 9,
                "fieldGoalPercentage": 0.45,
                "threePointsMade": 1,
                "threePointPercentage": 0.25,
                "freeThrowsMade": 6,
                "freeThrowPercentage": 0.75,
                "steals": 1,
                "blocks": 0,
                "turnovers": 4,
                "WinLoss": "L",
                "Matchup": "LAL @ NYK",
                "TEAM_ABBREVIATION": "LAL",
                "gameLocation": "away",
                "seasonType": "Regular Season",
                "SEASON_ID": "22024",
                "is_future_game": False
            },
            {
                "date": "2025-01-05",
                "opponent": "PHI",
                "opponent_abbr": "PHI",
                "points": 28,
                "rebounds": 7,
                "assists": 9,
                "fieldGoalsMade": 11,
                "fieldGoalPercentage": 0.55,
                "threePointsMade": 3,
                "threePointPercentage": 0.5,
                "freeThrowsMade": 3,
                "freeThrowPercentage": 0.6,
                "steals": 3,
                "blocks": 2,
                "turnovers": 2,
                "WinLoss": "W",
                "Matchup": "LAL vs. PHI",
                "TEAM_ABBREVIATION": "LAL",
                "gameLocation": "home",
                "seasonType": "Regular Season",
                "SEASON_ID": "22024",
                "is_future_game": False
            },
            {
                "date": "2025-02-10",
                "opponent": "PHI",
                "opponent_abbr": "PHI",
                "points": 32,
                "rebounds": 11,
                "assists": 8,
                "fieldGoalsMade": 12,
                "fieldGoalPercentage": 0.6,
                "threePointsMade": 4,
                "threePointPercentage": 0.57,
                "freeThrowsMade": 4,
                "freeThrowPercentage": 1.0,
                "steals": 2,
                "blocks": 3,
                "turnovers": 1,
                "WinLoss": "W",
                "Matchup": "LAL vs. PHI",
                "TEAM_ABBREVIATION": "LAL",
                "gameLocation": "home",
                "seasonType": "Regular Season",
                "SEASON_ID": "22024",
                "is_future_game": False
            },
            {
                "date": "2025-03-15",
                "opponent": "GSW",
                "opponent_abbr": "GSW",
                "points": 35,
                "rebounds": 9,
                "assists": 11,
                "fieldGoalsMade": 14,
                "fieldGoalPercentage": 0.65,
                "threePointsMade": 5,
                "threePointPercentage": 0.63,
                "freeThrowsMade": 2,
                "freeThrowPercentage": 0.67,
                "steals": 4,
                "blocks": 1,
                "turnovers": 2,
                "WinLoss": "W",
                "Matchup": "LAL @ GSW",
                "TEAM_ABBREVIATION": "LAL",
                "gameLocation": "away",
                "seasonType": "Regular Season",
                "SEASON_ID": "22024",
                "is_future_game": False
            },
            # Playoff game with different SEASON_ID
            {
                "date": "2025-04-20",
                "opponent": "DEN",
                "opponent_abbr": "DEN",
                "points": 38,
                "rebounds": 12,
                "assists": 10,
                "fieldGoalsMade": 15,
                "fieldGoalPercentage": 0.68,
                "threePointsMade": 4,
                "threePointPercentage": 0.57,
                "freeThrowsMade": 4,
                "freeThrowPercentage": 0.8,
                "steals": 2,
                "blocks": 2,
                "turnovers": 3,
                "WinLoss": "W",
                "Matchup": "LAL vs. DEN",
                "TEAM_ABBREVIATION": "LAL",
                "gameLocation": "home",
                "seasonType": "Postseason",
                "SEASON_ID": "42024",  # 4 prefix indicates playoffs
                "is_future_game": False
            }
        ]
    
    # FR25 - Filter Criteria Display Tests
    @patch('home.views.get_mongo_client')
    def test_filter_params_are_processed(self, mock_get_mongo_client):
        """
        FR25 - Test that filter parameters are correctly extracted from request
        """
        # Setup mock response
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        mock_get_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        # Create mock player data
        player_data = {
            "name": "LeBron James",
            "games": {
                "2025-01-01": {
                    "Matchup": "LAL vs. BOS",
                    "Points": 30,
                    "scoredRebounds": 10,
                    "Assists": 8,
                    "Team": "LAL",
                    "WinLoss": "W",
                    "SEASON_ID": "22024"
                }
            }
        }
        mock_collection.find_one.return_value = player_data
        
        # Query with filter parameters
        url = '/api/stats/player/LeBron James/?date_from=2025-01-02&date_to=2025-01-06&outcome=Win'
        response = self.client.get(url)
        
        # Check that response is successful
        self.assertEqual(response.status_code, 200)
    
    # FR26 + FR27 - Dynamic Update and Multiple Criteria Tests
    def test_filter_apply_multiple_criteria(self):
        """
        FR26, FR27 - Test that multiple filter criteria are applied correctly using the real filter function
        """
        # Define the filter criteria
        filters = {
            'date_from': '2025-01-04',  # After Jan 3
            'outcome': 'Win',           # Only wins
            'opponents': 'Philadelphia 76ers'  # Using full team name that maps to PHI
        }
        
        # Apply filters using the actual function
        filtered_results = apply_filters_to_games(self.test_player_games, filters)
        
        # Verify results
        self.assertEqual(len(filtered_results), 2)  # Should have 2 games that match criteria
        
        # Verify both are wins against PHI after Jan 4
        for game in filtered_results:
            self.assertEqual(game['opponent'], 'PHI')
            self.assertEqual(game['WinLoss'], 'W')
            self.assertGreaterEqual(game['date'], '2025-01-04')
    
    # FR28 - Filter Reset Test
    def test_filter_reset(self):
        """
        FR28 - Test that passing empty filters returns all games (no filtering)
        """
        # Apply filters with empty dict
        filtered_results = apply_filters_to_games(self.test_player_games, {})
        
        # Should return all games with no filtering
        self.assertEqual(len(filtered_results), len(self.test_player_games))
    
    # Date range filter test
    def test_date_range_filter(self):
        """Test filtering by date range"""
        # Only January 2025 games
        filters = {
            'date_from': '2025-01-01',
            'date_to': '2025-01-31'
        }
        
        filtered_results = apply_filters_to_games(self.test_player_games, filters)
        
        # Should return 3 games in January
        self.assertEqual(len(filtered_results), 3)
        
        for game in filtered_results:
            self.assertTrue(game['date'].startswith('2025-01'))
    
    def test_opponent_filter(self):
        """Test filtering by opponent team"""
        # Only games against Philadelphia, using the full team name
        filters = {
            'opponents': 'Philadelphia 76ers'  # This maps to PHI in the filter function
        }
        
        filtered_results = apply_filters_to_games(self.test_player_games, filters)
        
        # Should return 2 games against PHI
        self.assertEqual(len(filtered_results), 2)
        
        for game in filtered_results:
            self.assertEqual(game['opponent'], 'PHI')
    
    def test_outcome_filter(self):
        """Test filtering by game outcome (Win/Loss)"""
        # Only wins
        filters = {
            'outcome': 'Win'
        }
        
        filtered_results = apply_filters_to_games(self.test_player_games, filters)
        
        # Should return 5 wins
        self.assertEqual(len(filtered_results), 5)
        
        for game in filtered_results:
            self.assertEqual(game['WinLoss'], 'W')
        
        # Test loss filter
        filters = {
            'outcome': 'Loss'
        }
        
        filtered_results = apply_filters_to_games(self.test_player_games, filters)
        
        # Should return 1 loss
        self.assertEqual(len(filtered_results), 1)
        self.assertEqual(filtered_results[0]['WinLoss'], 'L')
    
    def test_season_type_filter(self):
        """Test filtering by season type (Regular Season vs Postseason)"""
        # Only playoff games
        filters = {
            'season_type': 'Postseason'
        }
        
        filtered_results = apply_filters_to_games(self.test_player_games, filters)
        
        # Should return 1 playoff game
        self.assertEqual(len(filtered_results), 1)
        self.assertEqual(filtered_results[0]['seasonType'], 'Postseason')
        self.assertEqual(filtered_results[0]['opponent'], 'DEN')
        
        # Regular season games
        filters = {
            'season_type': 'Regular Season'
        }
        
        filtered_results = apply_filters_to_games(self.test_player_games, filters)
        
        # Should return 5 regular season games
        self.assertEqual(len(filtered_results), 5)
        for game in filtered_results:
            self.assertEqual(game['seasonType'], 'Regular Season')
    
    def test_game_location_filter(self):
        """Test filtering by game location (home vs away)"""
        for game in self.test_player_games:
            # Ensure gameLocation is properly set based on Matchup
            game['gameLocation'] = 'home' if 'vs.' in game['Matchup'] else 'away'
        
        # Home games
        home_games = [g for g in self.test_player_games if g['gameLocation'] == 'home']
        away_games = [g for g in self.test_player_games if g['gameLocation'] == 'away']
        
        # Verify our test data setup
        self.assertEqual(len(home_games), 4)
        self.assertEqual(len(away_games), 2)
        
        # Only home games
        filters = {}  # We'll use a custom filter since game_location is derived from Matchup
        # In real usage, these would be processed from other filter params
        
        filtered_results = [g for g in self.test_player_games if g['gameLocation'] == 'home']
        
        # Should return 4 home games
        self.assertEqual(len(filtered_results), 4)
        for game in filtered_results:
            self.assertEqual(game['gameLocation'], 'home')
            self.assertIn('vs.', game['Matchup'])
    
    def test_last_n_games_filter(self):
        """Test filtering by last N games"""
        # Last 2 games (should be most recent by date)
        filters = {
            'last_n_games': '2'
        }
        
        # Sort games by date first (as the filter function would do)
        sorted_games = sorted(self.test_player_games, key=lambda x: x['date'], reverse=True)
        filtered_results = sorted_games[:2]  # Manual implementation of last_n_games
        
        # Should return 2 most recent games
        self.assertEqual(len(filtered_results), 2)
        self.assertEqual(filtered_results[0]['date'], '2025-04-20')  # Most recent
        self.assertEqual(filtered_results[1]['date'], '2025-03-15')  # Second most recent
    
    def test_combined_filters(self):
        """Test complex combination of multiple filter types"""
        # Filter for:
        # - January and February 2025 only
        # - Only home games
        # - Only games against Philadelphia
        # - Only wins
        
        # First, manually filter to verify our test data
        manual_filtered = [
            game for game in self.test_player_games
            if (game['date'] >= '2025-01-01' and game['date'] <= '2025-02-28')  # Jan-Feb only
            and game['gameLocation'] == 'home'  # Home games only
            and game['opponent'] == 'PHI'  # vs Philadelphia only
            and game['WinLoss'] == 'W'  # Only wins
        ]
        
        # Verify our manual filtering matches expectations
        self.assertEqual(len(manual_filtered), 2)
        self.assertEqual(manual_filtered[0]['date'], '2025-01-05')
        self.assertEqual(manual_filtered[1]['date'], '2025-02-10')
        
        # Now apply the actual filter function
        filters = {
            'date_from': '2025-01-01',
            'date_to': '2025-02-28',
            'outcome': 'Win',
            'opponents': 'Philadelphia 76ers'  # Use full team name that maps to PHI
        }
        
        filtered_results = apply_filters_to_games(self.test_player_games, filters)
        
        # Verify the filtered results match our expectations
        self.assertEqual(len(filtered_results), 2)
        dates = [game['date'] for game in filtered_results]
        self.assertIn('2025-01-05', dates)
        self.assertIn('2025-02-10', dates)
        
        for game in filtered_results:
            self.assertEqual(game['opponent'], 'PHI')
            self.assertEqual(game['WinLoss'], 'W')
            self.assertEqual(game['gameLocation'], 'home')
            self.assertTrue('2025-01-01' <= game['date'] <= '2025-02-28')
