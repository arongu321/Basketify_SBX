import unittest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
import json
import os

import feedback_loop

class TestFeedbackLoop(unittest.TestCase):

    ### ────────────────────────────────
    ### GROUP 1: Mongo Client Connection
    ### ────────────────────────────────

    @patch("feedback_loop.MongoClient")
    def test_get_mongo_client_success(self, mock_client):
        """Test successful MongoDB connection."""
        feedback_loop.mongo_client = None
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        result = feedback_loop.get_mongo_client()
        self.assertEqual(result, mock_instance)
        mock_client.assert_called_once()

    @patch("feedback_loop.MongoClient")
    def test_get_mongo_client_failure(self, mock_client):
        """Test MongoDB connection failure returns None."""
        feedback_loop.mongo_client = None
        mock_client.side_effect = Exception("Connection Error")

        result = feedback_loop.get_mongo_client()
        self.assertIsNone(result)

    ### ────────────────────────────────
    ### GROUP 2: store_feedback() Logic
    ### ────────────────────────────────

    @patch("feedback_loop.get_mongo_client")
    @patch("feedback_loop.datetime")
    def test_store_feedback_skips_old_data(self, mock_datetime, mock_get_client):
        """Ensure store_feedback skips games before last_run."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock now & last_run
        mock_now = datetime(2025, 4, 10)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.min = datetime.min
        mock_datetime.strptime = datetime.strptime

        # Setup DB structure
        mock_nba_db = MagicMock()
        mock_feedback_db = MagicMock()
        mock_client.__getitem__.side_effect = lambda x: mock_nba_db if x == 'nba_stats' else mock_feedback_db

        # Setup collection routing
        mock_players = MagicMock()
        mock_teams = MagicMock()
        mock_nba_db.__getitem__.side_effect = lambda x: mock_players if x == 'players' else mock_teams

        mock_player_feedback = MagicMock()
        mock_team_feedback = MagicMock()
        mock_meta = MagicMock()
        mock_feedback_db.__getitem__.side_effect = lambda x: {
            'player_predictions': mock_player_feedback,
            'team_predictions': mock_team_feedback,
            'meta': mock_meta
        }[x]

        # Mock meta document
        mock_meta.find_one.return_value = {"value": "2025-04-08_00-00-00"}

        # Game inside and outside range
        mock_players.find.return_value = [{
            "name": "Test Player",
            "future_games": {
                "2025-04-01_00-00-00": {"Points": 10},  # too old
                "2025-04-09_00-00-00": {"Points": 20}   # valid
            }
        }]
        mock_teams.find.return_value = []

        feedback_loop.store_feedback()

        mock_player_feedback.update_one.assert_called_once_with(
            {"name": "Test Player"},
            {"$set": {"future_games.2025-04-09_00-00-00": {"Points": 20}}},
            upsert=True
        )
        mock_meta.update_one.assert_called_once_with(
            {"key": "last_feedback_run"},
            {"$set": {"value": mock_now.strftime("%Y-%m-%d_%H-%M-%S")}},
            upsert=True
        )

    ### ──────────────────────────────────────────────
    ### GROUP 3: evaluate_feedback_discrepancies Logic
    ### ──────────────────────────────────────────────

    @patch("feedback_loop.get_mongo_client")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("os.makedirs")
    def test_evaluate_feedback_discrepancies(self, mock_makedirs, mock_json_dump, mock_open, mock_get_client):
        """Test large error results in -0.5 slider and report entry."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_nba_db = MagicMock()
        mock_feedback_db = MagicMock()
        mock_client.__getitem__.side_effect = lambda x: mock_nba_db if x == 'nba_stats' else mock_feedback_db

        mock_players_col = MagicMock()
        mock_teams_col = MagicMock()
        mock_nba_db.__getitem__.side_effect = lambda x: mock_players_col if x == 'players' else mock_teams_col

        mock_player_feedback = MagicMock()
        mock_team_feedback = MagicMock()
        mock_feedback_db.__getitem__.side_effect = lambda x: {
            'player_predictions': mock_player_feedback,
            'team_predictions': mock_team_feedback
        }[x]

        mock_player_feedback.find.return_value = [{
            "name": "Test Player",
            "future_games": {
                "2025-04-01_00-00-00": {"Points": 100}
            }
        }]
        mock_team_feedback.find.return_value = [{
            "name": "Test Team",
            "future_games": {
                "2025-04-01_00-00-00": {"Points": 120}
            }
        }]

        mock_players_col.find_one.return_value = {
            "games": {"2025-04-01_00-00-00": {"Points": 60}}
        }
        mock_teams_col.find_one.return_value = {
            "games": {"2025-04-01_00-00-00": {"Points": 105}}
        }

        feedback_loop.evaluate_feedback_discrepancies()

        mock_players_col.update_one.assert_called_once_with(
            {"name": "Test Player"},
            {"$set": {"slider": -0.5}}
        )
        mock_teams_col.update_one.assert_not_called()

        args, _ = mock_json_dump.call_args
        report = args[0]
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["slider_adjustment"], -0.5)

    @patch("feedback_loop.get_mongo_client")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("os.makedirs")
    def test_evaluate_feedback_medium_error(self, mock_makedirs, mock_json_dump, mock_open, mock_get_client):
        """Test 20-35% error results in ±0.25 slider."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_nba_db = MagicMock()
        mock_feedback_db = MagicMock()
        mock_client.__getitem__.side_effect = lambda x: mock_nba_db if x == 'nba_stats' else mock_feedback_db

        mock_players_col = MagicMock()
        mock_nba_db.__getitem__.return_value = mock_players_col

        mock_player_feedback = MagicMock()
        mock_team_feedback = MagicMock()
        mock_feedback_db.__getitem__.side_effect = lambda x: {
            'player_predictions': mock_player_feedback,
            'team_predictions': mock_team_feedback
        }[x]

        mock_player_feedback.find.return_value = [{
            "name": "Medium Error Player",
            "future_games": {
                "2025-04-01_00-00-00": {"Points": 25}
            }
        }]
        mock_players_col.find_one.return_value = {
            "games": {"2025-04-01_00-00-00": {"Points": 32}}
        }

        feedback_loop.evaluate_feedback_discrepancies()

        mock_players_col.update_one.assert_called_once_with(
            {"name": "Medium Error Player"},
            {"$set": {"slider": 0.25}}
        )

        args, _ = mock_json_dump.call_args
        report = args[0]
        self.assertEqual(report[0]["slider_adjustment"], 0.25)

    @patch("feedback_loop.get_mongo_client")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("os.makedirs")
    def test_evaluate_feedback_no_points_field(self, mock_makedirs, mock_json_dump, mock_open, mock_get_client):
        """Test feedback data missing Points field does not break logic."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_nba_db = MagicMock()
        mock_feedback_db = MagicMock()
        mock_client.__getitem__.side_effect = lambda x: mock_nba_db if x == 'nba_stats' else mock_feedback_db

        mock_players_col = MagicMock()
        mock_nba_db.__getitem__.return_value = mock_players_col

        mock_player_feedback = MagicMock()
        mock_team_feedback = MagicMock()
        mock_feedback_db.__getitem__.side_effect = lambda x: {
            'player_predictions': mock_player_feedback,
            'team_predictions': mock_team_feedback
        }[x]

        mock_player_feedback.find.return_value = [{
            "name": "No Points Player",
            "future_games": {"2025-04-01_00-00-00": {"Assists": 5}}
        }]
        mock_players_col.find_one.return_value = {
            "games": {"2025-04-01_00-00-00": {"Assists": 8}}
        }

        feedback_loop.evaluate_feedback_discrepancies()

        mock_players_col.update_one.assert_not_called()
        args, _ = mock_json_dump.call_args
        self.assertEqual(len(args[0]), 0)  # No reports generated

if __name__ == "__main__":
    unittest.main()
