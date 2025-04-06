import json
from pymongo import MongoClient
import datetime

mongo_client = None

# MongoDB connection function
def get_mongo_client():
    global mongo_client
    # check if mongo client is already initialized
    if mongo_client is not None:
        return mongo_client
    
    # remote Atlas DB
    uri = "mongodb+srv://zschmidt:ECE493@basketifycluster.dr6oe.mongodb.net"

    try:
        mongo_client = MongoClient(uri)
    except Exception as e:
        print(f"Couldn't connect to mongodb database at URI: {uri}")
        print(f"Error: {e}")
        return None
    
    print("Successfully connected")
    return mongo_client

# Insert data from JSON file (works for both teams and players)
def insert_data_from_json(json_file_path, collection_name, drop_collection=False):
    # Connect to MongoDB
    client = get_mongo_client()
    if client is None:
        raise Exception("Couldn't connect to MongoDB database")
    
    # Access the specified database
    db = client["nba_stats_all"]
    
    if drop_collection:
        # Drop the entire collection if it exists
        try:
            db.drop_collection(collection_name)
            print(f"Dropped existing {collection_name} collection")
        except Exception as e:
            print(f"Error dropping collection: {e}")
    
    # Reference to the collection
    collection = db[collection_name]
    
    # Load the JSON data
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        print(f"Loaded JSON file with {len(data)} {collection_name}")
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return
    
    # Insert each entity
    inserted_count = 0
    
    for entity_id, entity_data in data.items():
        try:
            team_data = {
                "_id": entity_id,
                "profile": entity_data["profile"]
            }
            collection.insert_one(
                team_data
            )

            # Insert exactly as is (with name field)
            for game in entity_data["games"]:
                date = game["GAME_DATE"]

                # Sanitize data format
                if not date or not isinstance(date, str):
                    print(f"Skipping game with invalid date: {date}")
                    continue
                    
                formatted_date = date.replace('/', '-').replace(' ', '_')

                game_data = {
                    "TEAM_ID": game["TEAM_ID"],
                    "TEAM_NAME": game["TEAM_NAME"],
                    "TEAM_ABBREVIATION": game["TEAM_ABBREVIATION"],
                    "GAME_ID": game["GAME_ID"],
                    "MATCHUP": game["MATCHUP"],
                    "MIN": game["MIN"],
                    "PTS": game["PTS"],
                    "FGM": game["FGM"],
                    "FGA": game["FGA"],
                    "FG_PCT": game["FG_PCT"],
                    "FG3M": game["FG3M"],
                    "FG3A": game["FG3A"],
                    "FG3_PCT": game["FG3_PCT"],
                    "FTM": game["FTM"],
                    "FTA": game["FTA"],
                    "FT_PCT": game["FT_PCT"],
                    "OREB": game["OREB"],
                    "DREB": game["DREB"],
                    "REB": game["REB"],
                    "AST": game["AST"],
                    "STL": game["STL"],
                    "BLK": game["BLK"],
                    "TOV": game["TOV"],
                    "PF": game["PF"],
                    "PLUS_MINUS": game["PLUS_MINUS"],
                    "GAME_LOCATION": game["GAME_LOCATION"],
                    "OPPONENT": game["OPPONENT"],
                    "OPPONENT_NAME": game["OPPONENT_NAME"],
                    "OPPONENT_DIVISION": game["OPPONENT_DIVISION"],
                    "OPPONENT_CONFERENCE": game["OPPONENT_CONFERENCE"],
                    "CONFERENCE_GAME": game["CONFERENCE_GAME"],
                    "DIVISION_GAME": game["DIVISION_GAME"],
                    "SEASON_TYPE": game["SEASON_TYPE"],
                    "SEASON_YEAR": game["SEASON_YEAR"],
                    "WINLOSS": game["WL"],
                    "is_future_game": False,
                }

                collection.update_one(
                    {"_id": entity_id},
                    {"$set": {f"games.{formatted_date}": game_data}},
                )

                print(f"Inserted game data for {entity_id} on {formatted_date}")
                
            inserted_count += 1
            print(f"Inserted all games for {entity_id}")
            
        except Exception as e:
            print(f"Error inserting {entity_id}: {e}")
    
    # Print results
    print(f"Inserted {inserted_count} {collection_name}")
    total_count = collection.count_documents({})
    print(f"Total documents in {collection_name} collection: {total_count}")