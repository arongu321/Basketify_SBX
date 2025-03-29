from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import players, teams
from pymongo import MongoClient
import requests
from datetime import datetime
from time import sleep
from ml.player_pred import predict_next_game_vs_team

# Setup MongoDB
try:
    client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
    print("Connected to MongoDB!")
except Exception as e:
    print("Error connecting to MongoDB:", e)

db = client['nba_stats']
game_collection = db['games']
player_collection = db['players']
team_collection = db['teams']

def get_player_data():
    all_players = players.get_players()
    
    for player in all_players:
        player_name = player['full_name']
        
        # Example: Get games for the player (You can specify season and filters here)
        try:
            game_finder = leaguegamefinder.LeagueGameFinder(player_id_nullable=player['id'], timeout=3, date_from_nullable="09/30/2009")
        except:
            print("Skipped")
            continue
        games = game_finder.get_data_frames()[0]

        most_recent_game = datetime(2000,1,1)
        current_team = None

        for _, game in games.iterrows():
            date = game['GAME_DATE']
            if datetime.strptime(date, "%Y-%m-%d") > most_recent_game:
                current_team = game['TEAM_ABBREVIATION']
            
            # Sanitize date format
            if not date or not isinstance(date, str):
                print(f"Skipping game with invalid date: {date}")
                continue
            formatted_date = date.replace('/', '-').replace(' ', '_')

            player_data = {
                "Matchup": game["MATCHUP"],
                "Points": game['PTS'],
                "scoredRebounds": game['REB'],
                "Assists": game['AST'],
                "FG_scored": game['FGM'],
                "FG_pctg": game['FG_PCT'],
                "3_pts_scored": game['FG3M'],
                "3_pts_pctg": game['FG3_PCT'],
                "FT_made": game['FTM'],
                "FT_pctg": game['FT_PCT'],
                "Steals": game['STL'],
                "Blocks": game['BLK'],
                "Turnovers": game['TOV'],
                "Team": game['TEAM_ABBREVIATION'],
                "WinLoss": game['WL'],
                "is_future_game": False
            }

            # Write to MongoDB after each game (update the player's document with a nested 'games' field)
            player_collection.update_one(
                {"name": player_name},
                {"$set": {
                    "team": current_team,
                    "games." + formatted_date: player_data
                }},
                upsert=True  # Keyword argument for upsert
            )

        sleep(0.5)

        print("Finished stats for player " + player['full_name'])


def get_team_data():
    all_teams = teams.get_teams()
    
    for team in all_teams:
        team_name = team['full_name']
        
        # Example: Get games for the team (You can specify season and filters here)
        try:
            game_finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team['id'], timeout=3, date_from_nullable = "09/30/2009")
        except:
            print("Skip: " + team_name)
            continue
        games = game_finder.get_data_frames()[0]
        
        for _, game in games.iterrows():
            date = game['GAME_DATE']

            # Sanitize date format
            if not date or not isinstance(date, str):
                print(f"Skipping game with invalid date: {date}")
                continue
            formatted_date = date.replace('/', '-').replace(' ', '_')
            
            team_data = {
                "Matchup": game["MATCHUP"],
                "Points": game['PTS'],
                "scoredRebounds": game['REB'],
                "Assists": game['AST'],
                "FG_scored": game['FGM'],
                "FG_pctg": game['FG_PCT'],
                "3_pts_scored": game['FG3M'],
                "3_pts_pctg": game['FG3_PCT'],
                "FT_made": game['FTM'],
                "FT_pctg": game['FT_PCT'],
                "Steals": game['STL'],
                "Blocks": game['BLK'],
                "Turnovers": game['TOV'],
                "WinLoss": game['WL'],
                "is_future_game": False
            }

            # Write to MongoDB after each game (update the team's document with a nested 'games' field)
            team_collection.update_one(
                {"name": team_name},
                {"$set": {
                    "abbrev_name": game['TEAM_ABBREVIATION'],
                    "games." + formatted_date: team_data
                }},
                upsert=True
            )

        sleep(0.5)

        print("Finished stats for team " + team['full_name'])


def get_upcoming_games():
    """
    Fetch the upcoming NBA games from the provided URL and return games that are scheduled after the current date.
    """
    url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
    
    try:
        # Fetch the data from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Extract the list of games from the JSON response
        upcoming_games = []

        for game_date in data["leagueSchedule"]["gameDates"]:
            for game in game_date["games"]:
                game_date_utc = datetime.strptime(game["gameDateUTC"], "%Y-%m-%dT%H:%M:%SZ")
                
                # Only add games that are after the current date and time
                if game_date_utc >= datetime.utcnow():
                    if game["homeTeam"]["teamCity"] is not None:
                        game_info = {
                            "gameId": game["gameId"],
                            "gameDateUTC": game_date_utc,
                            "homeTeam": game["homeTeam"]["teamTricode"],
                            "awayTeam": game["awayTeam"]["teamTricode"],
                        }
                        upcoming_games.append(game_info)
                    else:
                        print("Skipping game (likely playoffs/all-stars): ")
                        print(game)

        return upcoming_games

    except requests.exceptions.RequestException as e:
        print(f"Error fetching schedule: {e}")
        return []

def make_future_predictions():
    """
    This function makes predictions for upcoming games for both players and teams.
    """
    # Fetch upcoming games
    upcoming_games = get_upcoming_games()
    
    # For each player, predict points for their upcoming games
    all_players = db['players'].find()
    
    for player in all_players:
        player_name = player['name']
        
        for game in upcoming_games:
            # Check if the player is involved in this upcoming game
            if game['homeTeam'] in player['team'] or game['awayTeam'] in player['team']:
                team = game['homeTeam'] if game['homeTeam'] in player['team'] else game['awayTeam']
                
                # Predict points for the player in the next game
                predicted_points, confidence = predict_next_game_vs_team(player_name, team, "Points", "player")
                
                formatted_date = game['gameDateUTC'].strftime("%Y-%m-%d_%H-%M-%S")
                player_data = {
                    "Matchup": f"{game['homeTeam']} vs {game['awayTeam']}",
                    "Predicted_Points": predicted_points,
                    "Confidence": confidence,
                    "is_future_game": True
                }
                
                # Store the predicted data for this game in MongoDB
                db['players'].update_one(
                    {"name": player_name},
                    {"$set": {"future_games." + formatted_date: player_data}},  # Store predictions under 'future_games'
                    upsert=True
                )
                print(f"Predicted points for {player_name} in upcoming game: {predicted_points}")

    # For each team, predict points for their upcoming games
    all_teams = db['teams'].find()
    
    for team in all_teams:
        full_team_name = team['name']
        team_name = team['abbrev_name']
        
        for game in upcoming_games:
            # Check if the team is playing in the upcoming game
            if game['homeTeam'] == team_name or game['awayTeam'] == team_name:
                opponent_team = game['awayTeam'] if game['homeTeam'] == team_name else game['homeTeam']
                
                # Predict points for the team in the next game
                predicted_points, confidence = predict_next_game_vs_team(team_name, opponent_team, "Points", "team")
                
                formatted_date = game['gameDateUTC'].strftime("%Y-%m-%d_%H-%M-%S")
                team_data = {
                    "Matchup": f"{game['homeTeam']} vs {game['awayTeam']}",
                    "Predicted_Points": predicted_points,
                    "Confidence": confidence,
                    "is_future_game": True
                }
                
                # Store the predicted data for this game in MongoDB
                db['teams'].update_one(
                    {"name": full_team_name},
                    {"$set": {"future_games." + formatted_date: team_data}},  # Store predictions under 'future_games'
                    upsert=True
                )
                print(f"Predicted points for {team_name} in upcoming game: {predicted_points}")


def upload_to_mongodb():
    # Call get_player_data and get_team_data, but data will be uploaded to MongoDB in the functions
    #get_player_data()
    #get_team_data()
    make_future_predictions()
    

if __name__ == "__main__":
    upload_to_mongodb()
 