import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import scipy.stats as stats
from pymongo import MongoClient
# import matplotlib.pyplot as plt

# global to prevent having to connect multiple times
mongo_client = None


def get_mongo_client():
    global mongo_client
    # check if mongo client is already initialized
    if mongo_client is not None:
        return mongo_client
    
    # remote Atlas DB
    uri = "mongodb+srv://zschmidt:ECE493@basketifycluster.dr6oe.mongodb.net"

    # local MongoDB
    # uri = "mongodb://localhost:27017"


    try:
        mongo_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    except:
        print("Couldn't connect to mongodb database at URI: " + uri)
        return None
    
    print("Successfully connected")
    return mongo_client

# Connect to MongoDB and fetch past games
client = get_mongo_client()
if client is None:
    print("Error: Could not connect to MongoDB")

db = client['nba_stats']

def get_game_stats(name, entity_type="player"):
    """
    Fetch past game statistics for a given player or team.
    Returns Points, scoredRebounds, and Assists for the last 10 games.
    """
    client = get_mongo_client()
    if client is None:
        print("Error: Could not connect to MongoDB")
        return []

    db = client['nba_stats_all']
    collection = db['players'] if entity_type == "player" else db['teams']

    data = collection.find_one(
        {"name": {"$regex": name, "$options": "i"}},
        {"games": 1, "_id": 0}
    )

    if not data or "games" not in data:
        print(f"No data found for {entity_type}: {name}")
        return []

    game_stats = []
    for date, stats in data["games"].items():
        if date.startswith("2025") or date.startswith("2024"):
            game_stats.append((
                date,
                {
                    "Points": stats.get("Points", 0),
                    "scoredRebounds": stats.get("scoredRebounds", 0),
                    "Assists": stats.get("Assists", 0),
                    "FG_scored": stats.get("FG_scored", 0),
                    "FG_pctg": stats.get("FG_pctg", 0),
                    "3_pts_scored": stats.get("3_pts_scored", 0),
                    "3_pts_pctg": stats.get("3_pts_pctg", 0),
                    "FT_made": stats.get("FT_made", 0),
                    "FT_pctg": stats.get("FT_pctg", 0),
                    "Steals": stats.get("Steals", 0),
                    "Blocks": stats.get("Blocks", 0),
                    "Turnovers": stats.get("Turnovers", 0),
                }
            ))

    game_stats.sort(key=lambda x: x[0])
    return game_stats[-10:]

def predict_next_game_vs_team(name, team, stat_key, entity_type, degree=2):
    """
    Predict the next game's points against a specific team using Polynomial Regression.
    Uses:
      - Player's overall season performance (2025)
      - Player's last 5 games against the given team (NOP)
    """
    game_stats = get_game_stats(name, entity_type)
    
    if len(game_stats) < 5:  # Ensure enough data points
        print(f"Not enough data to predict {name}'s next game against {team}.")
        return None, None

    collection = db['players'] if entity_type == "player" else db['teams']

    # Fetch entity data
    entity_data = collection.find_one(
        {"name": name},
        {"games": 1, "_id": 0}
    )

    if not entity_data or "games" not in entity_data:
        print(f"No data found for {entity_type}: {name}")
        return None, None

    # Extract past 5 games against the specified team
    team_game_stats = []
    for date, stats in entity_data["games"].items():
        if "Matchup" in stats and team in stats["Matchup"]:
            team_game_stats.append((date, stats.get(stat_key, 0)))

    # Keep only the last 5 games against this team
    team_game_stats = sorted(team_game_stats, key=lambda x: x[0])[-5:]

    # Ensure we have at least some history against the team
    if len(team_game_stats) < 2:
       print(f"Not enough games played against {team} for a meaningful prediction.")
       return None, None

    # Combine season stats & matchup stats
    combined_stats = 2*game_stats + team_game_stats

    # Convert to numerical indices
    X = np.array(range(len(combined_stats))).reshape(-1, 1)  # Game index
    # y = np.array([game[1][stat_key] if isinstance(game[1], dict) else game[1] for game in combined_stats])

#     y = np.array([
#     game[1][stat_key] if isinstance(game[1], dict) and isinstance(game[1].get(stat_key), (int, float)) 
#     else np.nan 
#     for game in combined_stats
# ])

#     # remove any rows where the target var y is NaN
#     valid_indices = ~np.isnan(y)  # mask that lists rows where target y is NaN
#     X = X[valid_indices]
#     y = y[valid_indices]
    y = np.array([
        float(game[1][stat_key]) if isinstance(game[1], dict) and game[1].get(stat_key) is not None
        else float(game[1]) if not isinstance(game[1], dict) and game[1] is not None
        else np.nan
        for game in combined_stats
    ])

    # remove any rows where the target var y is NaN
    valid_indices = ~np.isnan(y)  # mask that lists rows where target y is NaN
    X = X[valid_indices]
    y = y[valid_indices]

    if X.shape[0] == 0:
        print(f"Error: No valid data available for prediction for {name} against {team}.")
        return None, None

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

    predicted_points = max(predicted_points, 0)  # no stat can be < 0

    #     # Visualize the regression
    # plt.figure(figsize=(8, 5))
    # plt.scatter(X, y, color='blue', label='Actual Data')
    # plt.plot(X, model.predict(X_poly), color='red', label='Polynomial Fit')

    # # Plot prediction point
    # plt.scatter(len(combined_stats), predicted_points, color='green', marker='x', s=100, label='Next Game Prediction')

    # plt.title(f"{name} - {stat_key} vs Game Index\n(Next Game vs {team})")
    # plt.xlabel("Game Index")
    # plt.ylabel(stat_key)
    # plt.legend()
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()
    return round(predicted_points, 2), round(confidence * 100, 2)  # Return prediction & confidence %


def predict_next_game_vs_team_with_ci(name, team, stat_key, entity_type, degree=2):
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
    game_stats = get_game_stats(name, entity_type)

    if len(game_stats) < 5:  # Ensure enough data points
        return f"Not enough data to predict {name}'s next game against {team}."

    collection = db['players'] if entity_type == "player" else db['teams']

    # Fetch entity data
    entity_data = collection.find_one(
        {"name": {"$regex": name, "$options": "i"}},
        {"games": 1, "_id": 0}
    )

    if not entity_data or "games" not in entity_data:
        return f"No data found for {entity_type}: {name}"

    # Extract past 5 games against the specified team
    team_game_stats = []
    for date, statis in entity_data["games"].items():
        if "Matchup" in statis and team in statis["Matchup"]:
            team_game_stats.append((date, statis.get(stat_key, 0)))

    # Keep only the last 5 games against this team
    team_game_stats = sorted(team_game_stats, key=lambda x: x[0])[-5:]

    # Ensure we have at least some history against the team
    if len(team_game_stats) < 2:
        return f"Not enough games played against {team} for a meaningful prediction."

    # Combine season stats & matchup stats
    combined_stats = 2*game_stats + team_game_stats

    # Convert to numerical indices
    X = np.array(range(len(combined_stats))).reshape(-1, 1)  # Game index
    y = np.array([game[1][stat_key] if isinstance(game[1], dict) else game[1] for game in combined_stats])

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
    entities = [("LeBron James", "player"), ("Los Angeles Lakers", "team")]
    stat_keys = ["Points"]
    team = "GSW"

    for name, entity_type in entities:
        print(f"\n===== Predictions for {entity_type.upper()}: {name} =====")
        for stat in stat_keys:
            # print(f"\n--- {stat} Predictions ---")

            # predicted_lr, conf_lr = predict_next_game_points(name, stat, entity_type)
            # print(f"Linear Regression - {stat}: {predicted_lr} (Confidence: {conf_lr}%)")

            # predicted_poly, conf_poly = predict_next_game_points_poly(name, stat, entity_type)
            # print(f"Polynomial Regression - {stat}: {predicted_poly} (Confidence: {conf_poly}%)")

            # predicted_poly, conf_poly, ranges = predict_point_ranges_poly(name, stat, entity_type)
            # print(f"Polynomial Regression - {stat}: {predicted_poly} (Confidence: {conf_poly}%)")
            # for level, (low, high) in ranges.items():
            #     print(f"{level} Confidence Interval: {low} - {high} {stat}")

            predicted_vs_team, conf_vs_team = predict_next_game_vs_team(name, team, stat, entity_type)
            print(f"{stat} vs {team}: {predicted_vs_team} (Confidence: {conf_vs_team}%)")

            predicted_vs_team, conf_vs_team, ranges_vs_team = predict_next_game_vs_team_with_ci(name, team, stat, entity_type)
            print(f"{stat} vs {team}: {predicted_vs_team} (Confidence: {conf_vs_team}%)")
            for level, (low, high) in ranges_vs_team.items():
                print(f"{level} Confidence Interval vs {team}: {low} - {high} {stat}")
