from pymongo import MongoClient

# Connect to MongoDB
def get_mongo_client():
    try:
        # Connect to MongoDB Atlas
        uri = "mongodb+srv://zschmidt:ECE493@basketifycluster.dr6oe.mongodb.net"
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        print("Connected to MongoDB!")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

# First script: Clean games with invalid team abbreviations
def clean_invalid_team_games():
    client = get_mongo_client()
    if not client:
        return
    
    db = client['nba_stats_all']
    player_collection = db['players']
    
    # Valid team abbreviations
    team_conferences = {
        "NYK": "East", "BKN": "East", "BOS": "East", "PHI": "East", "TOR": "East",
        "CHI": "East", "CLE": "East", "DET": "East", "IND": "East", "MIL": "East",
        "ATL": "East", "CHA": "East", "MIA": "East", "ORL": "East", "WAS": "East",
        "DAL": "West", "HOU": "West", "MEM": "West", "NOP": "West", "SAS": "West",
        "DEN": "West", "MIN": "West", "OKC": "West", "POR": "West", "UTA": "West",
        "GSW": "West", "LAC": "West", "LAL": "West", "PHX": "West", "SAC": "West"
    }
    
    alias_abbreviations = {
        "NJN": "BKN",
        "NOH": "NOP",
    }
    
    valid_abbreviations = list(team_conferences.keys()) + list(alias_abbreviations.keys())
    
    print("Cleaning regular games with invalid team abbreviations...")
    cursor = player_collection.aggregate([
        {"$project": {
            "name": 1,
            "gamesKV": {"$objectToArray": {"$ifNull": ["$games", {}]}}
        }},
        {"$unwind": "$gamesKV"},
        {"$project": {
            "name": 1,
            "gameDate": "$gamesKV.k",
            "teamAbbr": "$gamesKV.v.Team",
            "matchup": "$gamesKV.v.Matchup"
        }},
        {"$match": {
            "$or": [
                {"teamAbbr": {"$nin": valid_abbreviations}},
                {"teamAbbr": {"$exists": False}}
            ]
        }}
    ])
    
    games_removed = 0
    for doc in cursor:
        player_name = doc.get('name')
        game_date = doc.get('gameDate')
        team_abbr = doc.get('teamAbbr', 'N/A')
        
        player_collection.update_one(
            {"name": player_name},
            {"$unset": {f"games.{game_date}": ""}}
        )
        games_removed += 1
        
        if games_removed % 100 == 0:
            print(f"Removed {games_removed} invalid regular games")
        elif games_removed < 10 or games_removed % 500 == 0:
            print(f"Removed game with invalid team '{team_abbr}' for player '{player_name}', date: {game_date}")
    
    print(f"\nFinished cleaning invalid teams. Total games removed: {games_removed}")

# Second script: Remove duplicate player entries
def remove_duplicate_players():
    client = get_mongo_client()
    if not client:
        return
    
    db = client['nba_stats_all']
    player_collection = db['players']
    
    print("\nFinding players with duplicate names...")
    # Find players with duplicate names
    cursor = player_collection.aggregate([
        # Group by name and count occurrences
        {"$group": {
            "_id": "$name",
            "count": {"$sum": 1},
            "documents": {"$push": {
                "id": "$_id",
                "game_count": {"$size": {"$objectToArray": {"$ifNull": ["$games", {}]}}},
                "future_game_count": {"$size": {"$objectToArray": {"$ifNull": ["$future_games", {}]}}}
            }}
        }},
        # Filter only groups with more than 1 document (duplicates)
        {"$match": {"count": {"$gt": 1}}},
        # Sort by name for readable output
        {"$sort": {"_id": 1}}
    ])
    
    duplicates_found = 0
    duplicates_removed = 0
    
    for doc in cursor:
        player_name = doc["_id"]
        duplicates_found += 1
        
        # Sort by number of games (descending)
        sorted_docs = sorted(
            doc["documents"], 
            key=lambda x: x["game_count"] + x["future_game_count"], 
            reverse=False
        )
        
        # Keep the entry with the most games, remove others
        docs_to_remove = sorted_docs[1:]
        
        print(f"\nDuplicate found: '{player_name}'")
        print(f"  Keeping document with {sorted_docs[0]['game_count']} games and {sorted_docs[0]['future_game_count']} future games")
        
        for doc_to_remove in docs_to_remove:
            doc_id = doc_to_remove["id"]
            print(f"  Removing document with {doc_to_remove['game_count']} games and {doc_to_remove['future_game_count']} future games")
            
            # Remove the duplicate document
            result = player_collection.delete_one({"_id": doc_id})
            if result.deleted_count == 1:
                duplicates_removed += 1
            else:
                print(f"  Error: Failed to delete document with ID {doc_id}")
    
    print(f"\nDuplicate player cleanup complete.")
    print(f"Found {duplicates_found} players with duplicate entries")
    print(f"Removed {duplicates_removed} duplicate documents")

def get_game_dates():
    client = get_mongo_client()
    if not client:
        return
    
    db = client['nba_stats_all']
    player_collection = db['players']
    
    # Get all game dates
    player = player_collection.find_one({"name": "LeBron James"})

    games = player.get("games", {})
    future_games = player.get("future_games", {})

    for game_date, game_data in games.items():
        # Extract date part if the format is YYYY-MM-DD_HH-MM-SS
            date_parts = game_date.split('_')
            date_only = date_parts[0] if len(date_parts) > 0 else game_date
            print(f"Game date: {date_only}")
    
    for game_date, game_data in future_games.items():
        # Extract date part if the format is YYYY-MM-DD_HH-MM-SS
            date_parts = game_date.split('_')
            date_only = date_parts[0] if len(date_parts) > 0 else game_date
            print(f"Future game date: {date_only}")

if __name__ == "__main__":
    # Run both cleanups
    # clean_invalid_team_games()
    # remove_duplicate_players()
    # print("\nAll cleanup operations completed.")
    get_game_dates()