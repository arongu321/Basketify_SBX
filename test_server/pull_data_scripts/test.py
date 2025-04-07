from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb+srv://zschmidt:ECE493@basketifycluster.dr6oe.mongodb.net")
db = client["nba_stats_all"]
teams_collection = db["teams"]

# Define the date range
start_date = datetime(2000, 8, 1)
end_date = datetime(2009, 7, 1)

season_years = ["2000-1", "2001-2", "2002-3", "2003-4", "2004-5", "2005-6", "2006-7", "2007-8", "2008-9"]
season_year_dict = {
    "2000-1": "2000-01",
    "2001-2": "2001-02",
    "2002-3": "2002-03",
    "2003-4": "2003-04",
    "2004-5": "2004-05",
    "2005-6": "2005-06",
    "2006-7": "2006-07",
    "2007-8": "2007-08",
    "2008-9": "2008-09",
}
# Track how many updates we make
updated_count = 0

# Loop through all teams
for team_doc in teams_collection.find():
    team_id = team_doc["_id"]
    games = team_doc.get("games", {})

    # Prepare a dictionary of updates
    updated_games = {}

    for date_str, game_data in games.items():
        try:
            game_date = datetime.strptime(date_str, "%Y-%m-%d")

            if start_date < game_date < end_date:
                if game_data.get("SEASON_YEAR") in season_years:
                    old_season_year = game_data["SEASON_YEAR"]
                    game_data["SEASON_YEAR"] = season_year_dict[old_season_year]
                    updated_games[date_str] = game_data

        except Exception as e:
            print(f"Skipping invalid date format in {team_id}: {date_str} - {e}")

    # If any games were updated, push the new subdocuments back to MongoDB
    if updated_games:
        for date_str, updated_game_data in updated_games.items():
            teams_collection.update_one(
                {"_id": team_id},
                {"$set": {f"games.{date_str}": updated_game_data}}
            )
            updated_count += 1
            print(f"Updated SEASON_YEAR for {team_id} on {date_str}")

print(f"Total games updated: {updated_count}")
