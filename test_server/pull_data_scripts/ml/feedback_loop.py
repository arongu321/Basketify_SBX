from datetime import datetime
from pymongo import MongoClient
import json
import os

# global to prevent having to connect multiple times
mongo_client = None

def get_mongo_client():
    global mongo_client
    if mongo_client is not None:
        return mongo_client
    
    # local MongoDB
    uri = "mongodb://localhost:27017"

    try:
        mongo_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        print("Successfully connected")
        return mongo_client
    except:
        print("Couldn't connect to mongodb database at URI: " + uri)
        return None

# FR23 and 24: This function helps store performance temporarily to be compared and used for the feedback loop
def store_feedback():
    """
    Test function: Store games from nba_stats DB into feedback_db for testing comparison logic.
    """
    client = get_mongo_client()
    if client is None:
        print("Error: Could not connect to MongoDB")
        return

    db = client['nba_stats']
    feedback_db = client['feedback_db']
    player_feedback = feedback_db['player_predictions']
    team_feedback = feedback_db['team_predictions']
    meta = feedback_db['meta']

    # For testing: Use hardcoded dates
    # last_run = datetime.strptime("2025-04-05_00-00-00", "%Y-%m-%d_%H-%M-%S")

    # Get last run from meta
    meta_doc = meta.find_one({"key": "last_feedback_run"})
    last_run = datetime.min if not meta_doc else datetime.strptime(meta_doc['value'], "%Y-%m-%d_%H-%M-%S")
    now = datetime.utcnow()
    now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    # print(f"Test mode: Moving games between {last_run} and {now} to feedback DB")
    print(f"Collecting predictions between {last_run} and {now}")

    # Process players: Get from games (not future_games) for testing
    players_processed = 0
    for player in db['players'].find():
        name = player.get('name')
        # For testing: using games instead of future_games
        # games = player.get('games', {})
        future_games = player.get('future_games', {})
        
        # Omit 'future_' if testing
        for date_str, stats in future_games.items():
            try:
                game_date = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
            except:
                try:
                    game_date = datetime.strptime(date_str, "%Y-%m-%d")
                except:
                    continue

            # For testing: Only grab games in our test window
            if last_run <= game_date < now:
                player_feedback.update_one(
                    {"name": name},
                    {"$set": {f"future_games.{date_str}": stats}},
                    upsert=True
                )
                players_processed += 1

    # Process teams: similar approach
    teams_processed = 0
    for team in db['teams'].find():
        name = team.get('name')
        # For testing: using games instead of future_games
        games = team.get('games', {})
        
        for date_str, stats in games.items():
            try:
                game_date = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
            except:
                continue

            if last_run <= game_date < now:
                team_feedback.update_one(
                    {"name": name},
                    {"$set": {f"future_games.{date_str}": stats}},
                    upsert=True
                )
                teams_processed += 1

    # Update meta with run time
    meta.update_one(
        {"key": "last_feedback_run"},
        {"$set": {"value": now_str}},
        upsert=True
    )

    print(f"Test data copied: {players_processed} player games and {teams_processed} team games")

# FR23 and 24: This function is run AFTER getting the updated game data and compares it to the forecasted values
def evaluate_feedback_discrepancies():
    """
    Compare values in nba_stats DB with predictions stored in feedback_db.
    For testing purposes, we manually modify some values in the database before running this.
    """
    client = get_mongo_client()
    if client is None:
        return
        
    feedback_db = client["feedback_db"]
    db = client['nba_stats']

    report_data = []

    for entity_type, feedback_col in [("player", "player_predictions"), ("team", "team_predictions")]:
        for doc in feedback_db[feedback_col].find():
            name = doc["name"]
            future_games = doc.get("future_games", {})

            for date_str, predicted in future_games.items():
                # Get actual game data from nba_stats
                collection = db['players'] if entity_type == "player" else db['teams']
                record = collection.find_one({"name": name})
                if not record:
                    continue
                    
                # Get actual stats from games
                actual = record.get("games", {}).get(date_str)
                if not actual:
                    continue

                if (
                    "Points" in predicted and "Points" in actual and
                    isinstance(predicted["Points"], (int, float)) and
                    isinstance(actual["Points"], (int, float))
                ):
                    pred_val = predicted["Points"]
                    act_val = actual["Points"]
                    
                    # Skip if actual value is zero to avoid division by zero
                    if act_val == 0:
                        continue
                                        
                    error = pred_val - act_val
                    percent_error = abs(error) / abs(act_val)

                    slider = 0
                    if 0.20 < percent_error <= 0.35:
                        slider = 0.25 if error < 0 else -0.25
                    elif percent_error > 0.35:
                        slider = 0.5 if error < 0 else -0.5
                    else:
                        continue  # skip updating/reporting if error is small

                    report_data.append({
                        "name": name,
                        "type": entity_type,
                        "game_date": date_str,
                        "predicted": round(pred_val, 2),
                        "actual": round(act_val, 2),
                        "error_percent": round(percent_error * 100, 2),
                        "slider_adjustment": slider
                    })

                    # Update in DB
                    collection.update_one(
                        {"name": name},
                        {"$set": {"slider": slider}}
                    )

    # Save report
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/feedback_errors_report.json"
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=4)

    print(f"Test evaluation complete. Found {len(report_data)} discrepancies above 20% threshold.")
    print(f"Report saved to: {report_path}")

if __name__ == "__main__":
    # First step: Copy data from nba_stats to feedback_db
    store_feedback()
    
    # Manual step (not in code): You would now manually modify some values 
    # in the nba_stats database to simulate actual results being different
    # from predictions
    # print("\nNow you should manually modify some values in nba_stats.players/teams")
    # print("to simulate differences between predictions and actual results.")
    # proceed = input("Press Enter when ready to evaluate discrepancies...")
    
    # Second step: Evaluate differences
    evaluate_feedback_discrepancies()