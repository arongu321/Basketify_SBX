import unittest
from unittest.mock import patch, MagicMock
import player_pred
import numpy as np

class TestPlayerPred(unittest.TestCase):
    # ==================== Mongo Client Tests ====================

    @patch("player_pred.MongoClient")
    def test_get_mongo_client(self, mock_client):
        """Test successful Mongo client initialization."""
        player_pred.mongo_client = None  # Reset global
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        result = player_pred.get_mongo_client()
        mock_client.assert_called_once()
        self.assertEqual(result, mock_instance)

    @patch("player_pred.MongoClient")
    def test_get_mongo_client_connection_error(self, mock_client):
        """Test Mongo client handling connection failure."""
        player_pred.mongo_client = None
        mock_client.side_effect = Exception("Connection failed")

        result = player_pred.get_mongo_client()
        self.assertIsNone(result)

    # ==================== Game Stats Fetching ====================

    @patch("player_pred.db")
    def test_get_game_stats_success(self, mock_db):
        """Test game stats retrieval when valid data is found."""
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {
            "games": {
                "2025-04-01_00-00-00": {"Points": 20, "scoredRebounds": 5, "Assists": 3},
                "2025-04-02_00-00-00": {"Points": 25, "scoredRebounds": 6, "Assists": 4}
            }
        }
        stats = player_pred.get_game_stats("LeBron James", "player")
        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0][1]["Points"], 20)

    @patch("player_pred.db")
    def test_get_game_stats_no_data(self, mock_db):
        """Test get_game_stats when no data is returned."""
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {}
        stats = player_pred.get_game_stats("Ghost Player", "player")
        self.assertEqual(stats, [])

    # ==================== Prediction with Confidence Interval ====================

    @patch("player_pred.db")
    def test_predict_next_game_vs_team_with_ci_valid(self, mock_db):
        """Test prediction with CI returns valid tuple for sufficient data."""
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        game_stats = {
            f"2025-04-0{i}_00-00-00": {"Points": 20 + i, "Matchup": "LAL vs GSW"}
            for i in range(1, 6)
        }

        mock_collection.find_one.side_effect = [
            {"games": game_stats},  # get_game_stats
            {"games": game_stats, "slider": 0.25},  # for prediction
        ]

        result = player_pred.predict_next_game_vs_team_with_ci("LeBron James", "GSW", "Points", "player", degree=2)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertGreaterEqual(result[0], 0)

    @patch("player_pred.db")
    def test_predict_next_game_vs_team_with_ci_not_enough_games(self, mock_db):
        """Test prediction returns None when insufficient history exists."""
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        game_stats = {
            "2025-04-01_00-00-00": {"Points": 20, "Matchup": "LAL vs GSW"}
        }

        mock_collection.find_one.side_effect = [
            {"games": game_stats},
            {"games": game_stats, "slider": 0}
        ]

        result = player_pred.predict_next_game_vs_team_with_ci("LeBron James", "GSW", "Points", "player", degree=2)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

    # ==================== Team Performance / Prediction Stats ====================

    @patch("player_pred.db")
    def test_team_ppg_calc(self, mock_db):
        """Test average PPG calculation for valid team data."""
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {
            "games": {
                "game1": {"Points": 90},
                "game2": {"Points": 110},
            },
            "future_games": {
                "game3": {"Points": 100},
            }
        }
        ppg = player_pred.team_ppg("GSW", "Points", "team")
        self.assertEqual(ppg, 100)

    @patch("player_pred.db")
    def test_team_ppg_no_points(self, mock_db):
        """Test PPG function when no point data exists."""
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {
            "games": {"game1": {}},
            "future_games": {"game2": {}}
        }
        ppg = player_pred.team_ppg("GSW", "Points", "team")
        self.assertIsNone(ppg)

    # ==================== Champion Prediction ====================

    @patch("player_pred.db")
    def test_predict_nba_champion(self, mock_db):
        """Test champion prediction with valid top-scoring team."""
        mock_db["teams"].find_one.return_value = {
            "name": "Golden State Warriors",
            "avg_ppg": 115
        }
        name, score = player_pred.predict_nba_champion()
        self.assertEqual(name, "Golden State Warriors")
        self.assertEqual(score, 115)

    @patch("player_pred.db")
    def test_predict_nba_champion_no_data(self, mock_db):
        """Test champion prediction when no avg_ppg data is available."""
        mock_db["teams"].find_one.return_value = None
        name, score = player_pred.predict_nba_champion()
        self.assertEqual(name, "No team has avg_ppg recorded")
        self.assertEqual(score, 0)

    # ==================== Win/Loss Prediction ====================

    @patch("player_pred.db")
    def test_determine_win_loss_logic(self, mock_db):
        """Test determine_win_loss returns 'W' when team score > opponent."""
        mock_db["teams"].find_one.side_effect = [
            {"future_games": {"2025-04-01_00-00-00": {"Points": 100}}},
            {"future_games": {"2025-04-01_00-00-00": {"Points": 90}}},
        ]
        result = player_pred.determine_win_loss("LAL", "GSW", "2025-04-01_00-00-00")
        self.assertEqual(result, "W")

    @patch("player_pred.db")
    def test_determine_win_loss_loss(self, mock_db):
        """Test determine_win_loss returns 'L' when team score < opponent."""
        mock_db["teams"].find_one.side_effect = [
            {"future_games": {"2025-04-01_00-00-00": {"Points": 90}}},
            {"future_games": {"2025-04-01_00-00-00": {"Points": 100}}},
        ]
        result = player_pred.determine_win_loss("LAL", "GSW", "2025-04-01_00-00-00")
        self.assertEqual(result, "L")

    @patch("player_pred.db")
    def test_determine_win_loss_tie(self, mock_db):
        """Test determine_win_loss returns 'T' when scores are equal."""
        mock_db["teams"].find_one.side_effect = [
            {"future_games": {"2025-04-01_00-00-00": {"Points": 100}}},
            {"future_games": {"2025-04-01_00-00-00": {"Points": 100}}},
        ]
        result = player_pred.determine_win_loss("LAL", "GSW", "2025-04-01_00-00-00")
        self.assertEqual(result, "T")

    @patch("player_pred.db")
    def test_determine_win_loss_team_not_found(self, mock_db):
        """Test win/loss function when teams not found in DB."""
        mock_db["teams"].find_one.side_effect = [None, None]
        result = player_pred.determine_win_loss("INVALID", "TEAM", "2025-04-01_00-00-00")
        self.assertEqual(result, "Error: One or both teams not found.")

    @patch("player_pred.db")
    def test_determine_win_loss_game_not_found(self, mock_db):
        """Test win/loss function when game date data is missing."""
        mock_db["teams"].find_one.side_effect = [
            {"future_games": {}},
            {"future_games": {"2025-04-01_00-00-00": {"Points": 90}}},
        ]
        result = player_pred.determine_win_loss("LAL", "GSW", "2025-04-01_00-00-00")
        self.assertEqual(result, "Error: Score not found for LAL or GSW on 2025-04-01_00-00-00")

if __name__ == "__main__":
    unittest.main()
