from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import players, teams
from pymongo import MongoClient
from time import sleep

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
            game_finder = leaguegamefinder.LeagueGameFinder(player_id_nullable=player['id'], timeout=3, date_from_nullable="01/01/2010")
        except:
            print("Skipped")
            continue
        games = game_finder.get_data_frames()[0]

        for _, game in games.iterrows():
            date = game['GAME_DATE']
            
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
                "WinLoss": game['WL']
            }

            # Write to MongoDB after each game (update the player's document with a nested 'games' field)
            player_collection.update_one(
                {"name": player_name},
                {"$set": {"games." + formatted_date: player_data}},  # Store game data under 'games'
                upsert=True
            )

        print("Finished stats for player " + player['full_name'])
        sleep(0.5)

    

def get_team_data():
    all_teams = teams.get_teams()
    
    for team in all_teams:
        team_name = team['full_name']
        
        # Example: Get games for the team (You can specify season and filters here)
        try:
            game_finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team['id'], timeout=3, date_from_nullable = "01/01/2010")
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
                "WinLoss": game['WL']
            }

            # Write to MongoDB after each game (update the team's document with a nested 'games' field)
            team_collection.update_one(
                {"name": team_name},
                {"$set": {"games." + 
                          team_name + "." +
                          formatted_date: team_data}},  # Store game data under 'games'
                upsert=True
            )

        print("Finished stats for team " + team['full_name'])
        sleep(0.5)


def upload_to_mongodb():
    # Call get_player_data and get_team_data, but data will be uploaded to MongoDB in the functions
    get_player_data()
    get_team_data()


if __name__ == "__main__":
    upload_to_mongodb()
