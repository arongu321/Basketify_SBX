import sys
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import scipy.stats as stats

# Get the absolute path of the backend directory
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(backend_path)

from home.views import get_mongo_client  # Import the existing connection function

def get_player_game_stats(name):
    """
    Fetch past game statistics for a given player.
    Extracts only the 'Points' from each game in the current season.
    """
    client = get_mongo_client()
    if client is None:
        print("Error: Could not connect to MongoDB")
        return []

    # Select the database and collection
    db = client['nba_stats']  # Ensure this is your correct DB name
    players_collection = db['players']  # Ensure this is your correct collection name

    # Query for the player (case-insensitive match)
    player_data = players_collection.find_one(
        {"name": {"$regex": name, "$options": "i"}},  # case-insensitive search
        {"games": 1, "_id": 0}  # Retrieve only the 'games' field
    )

    if not player_data or "games" not in player_data:
        print(f"No data found for player: {name}")
        return []

    # Extract points per game from the 'games' dictionary
    game_stats = []
    for date, stats in player_data["games"].items():
        if date.startswith("2025"):  # Filter only 2025 season games
            game_stats.append((date, stats.get("Points", 0)))  # Default to 0 if missing

    # Sort by date (oldest to newest)
    game_stats.sort(key=lambda x: x[0])

    recent_games = game_stats[-10:]

    return recent_games


def predict_next_game_points(player_name):
    """
    Predict the next game's points using Linear Regression and return confidence score.
    """
    game_stats = get_player_game_stats(player_name)

    if len(game_stats) < 5:  # Ensure enough data points
        return f"Not enough data to predict {player_name}'s next game points."

    # Convert dates to sequential numbers (e.g., Game 1, Game 2, ...)
    X = np.array(range(len(game_stats))).reshape(-1, 1)  # Game index
    y = np.array([points for _, points in game_stats])  # Points scored

    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict next game's points (extrapolate)
    next_game_index = np.array([[len(game_stats)]])  # Next game
    predicted_points = model.predict(next_game_index)[0]

    # Calculate confidence score (R² value)
    confidence = model.score(X, y)  # Ranges from 0 to 1

    return round(predicted_points, 2), round(confidence * 100, 2)  # Return prediction & confidence %

def predict_next_game_points_poly(player_name, degree=2):
    """
    Predict the next game's points using Polynomial Regression.
    Default degree = 2 (Quadratic fit).
    """
    game_stats = get_player_game_stats(player_name)

    if len(game_stats) < 5:  # Ensure enough data points
        return f"Not enough data to predict {player_name}'s next game points."

    # Convert game indices to numerical values
    X = np.array(range(len(game_stats))).reshape(-1, 1)  # Game index
    y = np.array([points for _, points in game_stats])  # Points scored

    # Transform features for Polynomial Regression
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)

    # Train Polynomial Regression model
    model = LinearRegression()
    model.fit(X_poly, y)

    # Predict next game's points
    next_game_index = np.array([[len(game_stats)]])
    next_game_poly = poly.transform(next_game_index)
    predicted_points = model.predict(next_game_poly)[0]

    # Calculate confidence score (R² value)
    confidence = model.score(X_poly, y)  # Ranges from 0 to 1

    return round(predicted_points, 2), round(confidence * 100, 2)  # Return prediction & confidence %

def predict_point_ranges_poly(player_name, degree=2):
    """
    Predict the next game's points using Polynomial Regression.
    Returns confidence intervals at 80%, 85%, and 90%.
    """
    game_stats = get_player_game_stats(player_name)

    if len(game_stats) < 5:  # Ensure enough data points
        return f"Not enough data to predict {player_name}'s next game points."

    # Convert game indices to numerical values
    X = np.array(range(len(game_stats))).reshape(-1, 1)  # Game index
    y = np.array([points for _, points in game_stats])  # Points scored

    # Transform features for Polynomial Regression
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)

    # Train Polynomial Regression model
    model = LinearRegression()
    model.fit(X_poly, y)

    # Predict next game's points
    next_game_index = np.array([[len(game_stats)]])
    next_game_poly = poly.transform(next_game_index)
    predicted_points = model.predict(next_game_poly)[0]

    # Calculate confidence score (R² value)
    confidence = model.score(X_poly, y)  # Ranges from 0 to 1

    # Calculate standard deviation of residuals
    residuals = y - model.predict(X_poly)
    std_dev = np.std(residuals)

    # Confidence intervals (80%, 85%, 90%)
    confidence_intervals = {
        "80%": stats.norm.ppf(0.90) * std_dev,  # 80% range
        "85%": stats.norm.ppf(0.925) * std_dev,  # 85% range
        "90%": stats.norm.ppf(0.95) * std_dev,  # 90% range
    }

    # Compute prediction ranges
    prediction_ranges = {
        level: (round(predicted_points - ci, 2), round(predicted_points + ci, 2))
        for level, ci in confidence_intervals.items()
    }

    return round(predicted_points, 2), round(confidence * 100, 2), prediction_ranges

def predict_next_game_vs_team(player_name, team, degree=2):
    """
    Predict the next game's points against a specific team using Polynomial Regression.
    Uses:
      - Player's overall season performance (2025)
      - Player's last 5 games against the given team (NOP)
    """
    game_stats = get_player_game_stats(player_name)
    
    if len(game_stats) < 5:  # Ensure enough data points
        return f"Not enough data to predict {player_name}'s next game against {team}."

    # Connect to MongoDB and fetch past games
    client = get_mongo_client()
    if client is None:
        return "Error: Could not connect to MongoDB"

    db = client['nba_stats']
    players_collection = db['players']

    # Fetch player data
    player_data = players_collection.find_one(
        {"name": {"$regex": player_name, "$options": "i"}},
        {"games": 1, "_id": 0}
    )

    if not player_data or "games" not in player_data:
        return f"No data found for player: {player_name}"

    # Extract past 5 games against the specified team
    team_game_stats = []
    for date, stats in player_data["games"].items():
        if "Matchup" in stats and team in stats["Matchup"]:
            team_game_stats.append((date, stats.get("Points", 0)))

    # Keep only the last 5 games against this team
    team_game_stats = sorted(team_game_stats, key=lambda x: x[0])[-5:]

    # Ensure we have at least some history against the team
    if len(team_game_stats) < 2:
        return f"Not enough games played against {team} for a meaningful prediction."

    # Combine season stats & matchup stats
    combined_stats = 2*game_stats + team_game_stats

    # Convert to numerical indices
    X = np.array(range(len(combined_stats))).reshape(-1, 1)  # Game index
    y = np.array([points for _, points in combined_stats])  # Points scored

    # Transform features for Polynomial Regression
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)

    # Train Polynomial Regression model
    model = LinearRegression()
    model.fit(X_poly, y)

    # Predict next game's points against the team
    next_game_index = np.array([[len(combined_stats)]])
    next_game_poly = poly.transform(next_game_index)
    predicted_points = model.predict(next_game_poly)[0]

    # Calculate confidence score (R² value)
    confidence = model.score(X_poly, y)  # Ranges from 0 to 1

    return round(predicted_points, 2), round(confidence * 100, 2)  # Return prediction & confidence %

import scipy.stats as stats

def predict_next_game_vs_team_with_ci(player_name, team, degree=2):
    """
    Predict the next game's points against a specific team using Polynomial Regression.
    Uses:
      - Player's overall season performance (2025)
      - Player's last 5 games against the given team (NOP)
    Returns:
      - Predicted points
      - Confidence score (R²)
      - Confidence intervals (80%, 85%, 90%)
    """
    game_stats = get_player_game_stats(player_name)

    if len(game_stats) < 5:  # Ensure enough data points
        return f"Not enough data to predict {player_name}'s next game against {team}."

    # Connect to MongoDB and fetch past games
    client = get_mongo_client()
    if client is None:
        return "Error: Could not connect to MongoDB"

    db = client['nba_stats']
    players_collection = db['players']

    # Fetch player data
    player_data = players_collection.find_one(
        {"name": {"$regex": player_name, "$options": "i"}},
        {"games": 1, "_id": 0}
    )

    if not player_data or "games" not in player_data:
        return f"No data found for player: {player_name}"

    # Extract past 5 games against the specified team
    team_game_stats = []
    for date, statis in player_data["games"].items():
        if "Matchup" in statis and team in statis["Matchup"]:
            team_game_stats.append((date, statis.get("Points", 0)))

    # Keep only the last 5 games against this team
    team_game_stats = sorted(team_game_stats, key=lambda x: x[0])[-5:]

    # Ensure we have at least some history against the team
    if len(team_game_stats) < 2:
        return f"Not enough games played against {team} for a meaningful prediction."

    # Combine season stats & matchup stats
    combined_stats = game_stats + team_game_stats

    # Convert to numerical indices
    X = np.array(range(len(combined_stats))).reshape(-1, 1)  # Game index
    y = np.array([points for _, points in combined_stats])  # Points scored

    # Transform features for Polynomial Regression
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)

    # Train Polynomial Regression model
    model = LinearRegression()
    model.fit(X_poly, y)

    # Predict next game's points against the team
    next_game_index = np.array([[len(combined_stats)]])
    next_game_poly = poly.transform(next_game_index)
    predicted_points = model.predict(next_game_poly)[0]

    # Calculate confidence score (R² value)
    confidence = model.score(X_poly, y)  # Ranges from 0 to 1

    # Calculate standard deviation of residuals
    residuals = y - model.predict(X_poly)
    std_dev = np.std(residuals)

    # Confidence intervals (80%, 85%, 90%)
    confidence_intervals = {
        "80%": stats.norm.ppf(0.90) * std_dev,  # 80% range
        "85%": stats.norm.ppf(0.925) * std_dev,  # 85% range
        "90%": stats.norm.ppf(0.95) * std_dev,  # 90% range
    }

    # Compute prediction ranges
    prediction_ranges = {
        level: (round(predicted_points - ci, 2), round(predicted_points + ci, 2))
        for level, ci in confidence_intervals.items()
    }

    return round(predicted_points, 2), round(confidence * 100, 2), prediction_ranges


if __name__ == "__main__":
    predicted_ppg_linear, confidence_linear = predict_next_game_points("LeBron James")
    predicted_ppg_poly, confidence_poly = predict_next_game_points_poly("LeBron James")

    print(f"Linear Regression - Predicted points for LeBron James' next game: {predicted_ppg_linear} (Confidence: {confidence_linear}%)")
    print(f"Polynomial Regression - Predicted points for LeBron James' next game: {predicted_ppg_poly} (Confidence: {confidence_poly}%)")

    predicted_ppg_poly, confidence_poly, ranges_poly = predict_point_ranges_poly("LeBron James")

    print(f"Polynomial Regression - Predicted points for LeBron James' next game: {predicted_ppg_poly} (Confidence: {confidence_poly}%)")
    
    print("Prediction Ranges:")
    for level, (low, high) in ranges_poly.items():
        print(f"{level} Confidence Interval: {low} - {high} points")

    team = "NOP"  # New Orleans Pelicans
    predicted_ppg_vs_team, confidence_vs_team = predict_next_game_vs_team("LeBron James", team)

    print(f"Predicted points for LeBron James' next game against {team}: {predicted_ppg_vs_team} (Confidence: {confidence_vs_team}%)")

    team = "NOP"  # New Orleans Pelicans
    predicted_ppg_vs_team, confidence_vs_team, ranges_vs_team = predict_next_game_vs_team_with_ci("LeBron James", team)

    print(f"Predicted points for LeBron James' next game against {team}: {predicted_ppg_vs_team} (Confidence: {confidence_vs_team}%)")

    print("Prediction Ranges:")
    for level, (low, high) in ranges_vs_team.items():
        print(f"{level} Confidence Interval: {low} - {high} points")
