from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import players, teams
from pymongo import MongoClient
import requests
from datetime import datetime
from time import sleep
from ml.player_pred import determine_win_loss, predict_nba_champion, predict_next_game_vs_team_with_ci, team_ppg
from ml.feedback_loop import evaluate_feedback_discrepancies, store_feedback
try:
    #client = MongoClient("mongodb+srv://zschmidt:ECE493@basketifycluster.dr6oe.mongodb.net", serverSelectionTimeoutMS=5000)
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
    print("Connected to MongoDB!")
except Exception as e:
    print("Error connecting to MongoDB:", e)

db = client['nba_stats']
player_collection = db['players']
team_collection = db['teams']


def get_player_data():
    all_players = players.get_active_players()
    
    for player in all_players:
        game_finder = None
        player_name = player['full_name']
        
        while game_finder is None:
            try:
                game_finder = leaguegamefinder.LeagueGameFinder(player_id_nullable=player['id'], timeout=3, date_from_nullable="10/01/2022")
            except:
                print("Skipped")
        games = game_finder.get_data_frames()[0]

        most_recent_game = datetime(2000,1,1)
        current_team = None

        for _, game in games.iterrows():
            date = game['GAME_DATE']
            game_date = datetime.strptime(date, "%Y-%m-%d")
            if game_date > most_recent_game:
                most_recent_game = game_date
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
                "SEASON_ID": game['SEASON_ID'],
                "is_future_game": False
            }

            player_collection.update_one(
                {"name": player_name},
                {"$set": {
                    "team": current_team,
                    "games." + formatted_date: player_data,
                    "slider": 0
                }},
                upsert=True
            )

        sleep(0.5)  # prevent API rate limiting

        print("Finished stats for player " + player['full_name'])


def get_team_data():
    all_teams = teams.get_teams()
    
    for team in all_teams:
        game_finder = None
        team_name = team['full_name']
        
        while game_finder is None:
            try:
                game_finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team['id'], timeout=3, date_from_nullable = "09/30/2009")
            except:
                print("Skip: " + team_name)
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
                "SEASON_ID": game['SEASON_ID'],
                "is_future_game": False
            }

            team_collection.update_one(
                {"name": team_name},
                {"$set": {
                    "abbrev_name": game['TEAM_ABBREVIATION'],
                    "games." + formatted_date: team_data,
                    "slider": 0.5
                }},
                upsert=True
            )

        sleep(0.5)  # prevent API rate limiting

        print("Finished stats for team " + team['full_name'])


def get_upcoming_games():
    """
    Fetch the upcoming NBA games from the provided URL and return games that are scheduled after the current date.
    """
    url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        upcoming_games = []

        for game_date in data["leagueSchedule"]["gameDates"]:
            for game in game_date["games"]:
                game_date_utc = datetime.strptime(game["gameDateUTC"], "%Y-%m-%dT%H:%M:%SZ")
                
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
    upcoming_games = get_upcoming_games()
    
    all_players = db['players'].find().batch_size(100)
    
    for player in all_players:
        player_name = player['name']
        
        for game in upcoming_games:
            if game['homeTeam'] in player['team'] or game['awayTeam'] in player['team']:
                opponent_team = game['awayTeam'] if game['homeTeam'] in player['team'] else game['homeTeam']
                
                if player['team'] == game['homeTeam']:
                    matchup = f"{game['homeTeam']} vs {game['awayTeam']}"
                else:
                    matchup = f"{game['awayTeam']} @ {game['homeTeam']}"
                predicted_points, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "Points", "player")
                predicted_rebounds, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "scoredRebounds", "player")
                predicted_assists, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "Assists", "player")
                predicted_fg, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "FG_scored", "player")
                predicted_fg_pctg, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "FG_pctg", "player")
                predicted_3, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "3_pts_scored", "player")
                predicted_3_pctg, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "3_pts_pctg", "player")
                predicted_ft, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "FT_made", "player")
                predicted_ft_pctg, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "FT_pctg", "player")
                predicted_steals, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "Steals", "player")
                predicted_blocks, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "Blocks", "player")
                predicted_turnovers, _ = predict_next_game_vs_team_with_ci(player_name, opponent_team, "Turnovers", "player")
                
                formatted_date = game['gameDateUTC'].strftime("%Y-%m-%d_%H-%M-%S")
                player_data = {
                    "Matchup": matchup,
                    "Points": predicted_points,
                    "scoredRebounds": predicted_rebounds,
                    "Assists": predicted_assists,
                    "FG_scored": predicted_fg,
                    "FG_pctg": predicted_fg_pctg,
                    "3_pts_scored": predicted_3,
                    "3_pts_pctg": predicted_3_pctg,
                    "FT_made": predicted_ft,
                    "FT_pctg": predicted_ft_pctg,
                    "Steals": predicted_steals,
                    "Blocks": predicted_blocks,
                    "Turnovers": predicted_turnovers,
                    "Team": player['team'],
                    "SEASON_ID": "22024",
                    "is_future_game": True
                }
                
                db['players'].update_one(
                    {"name": player_name},
                    {"$set": {"future_games." + formatted_date: player_data}},  # create new future_games collection
                    upsert=True
                )
                print(f"Predicted points for {player_name} in upcoming game: {predicted_points}")

    all_teams = db['teams'].find()
    
    for team in all_teams:
        full_team_name = team['name']
        team_name = team['abbrev_name']
        
        for game in upcoming_games:
            if game['homeTeam'] == team_name or game['awayTeam'] == team_name:
                opponent_team = game['awayTeam'] if game['homeTeam'] == team_name else game['homeTeam']
                
                predicted_points, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "Points", "team")
                predicted_rebounds, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "scoredRebounds", "team")
                predicted_assists, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "Assists", "team")
                predicted_fg, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "FG_scored", "team")
                predicted_fg_pctg, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "FG_pctg", "team")
                predicted_3, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "3_pts_scored", "team")
                predicted_3_pctg, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "3_pts_pctg", "team")
                predicted_ft, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "FT_made", "team")
                predicted_ft_pctg, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "FT_pctg", "team")
                predicted_steals, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "Steals", "team")
                predicted_blocks, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "Blocks", "team")
                predicted_turnovers, _ = predict_next_game_vs_team_with_ci(full_team_name, opponent_team, "Turnovers", "team")
                
                formatted_date = game['gameDateUTC'].strftime("%Y-%m-%d_%H-%M-%S")
                team_data = {
                    "Matchup": f"{game['homeTeam']} vs {game['awayTeam']}",
                    "Points": predicted_points,
                    "scoredRebounds": predicted_rebounds,
                    "Assists": predicted_assists,
                    "FG_scored": predicted_fg,
                    "FG_pctg": predicted_fg_pctg,
                    "3_pts_scored": predicted_3,
                    "3_pts_pctg": predicted_3_pctg,
                    "FT_made": predicted_ft,
                    "FT_pctg": predicted_ft_pctg,
                    "Steals": predicted_steals,
                    "Blocks": predicted_blocks,
                    "Turnovers": predicted_turnovers,
                    "Team": player['team'],
                    "SEASON_ID": "22024",
                    "is_future_game": True
                }

                db['teams'].update_one(
                    {"name": full_team_name},
                    {"$set": {"future_games." + formatted_date: team_data}},  # create new future_games collection
                    upsert=True
                )
                print(f"Predicted points for {team_name} in upcoming game: {predicted_points}")

        avg = team_ppg(team_name, "Points", "team")
        team_collection.update_one(
            {"name": full_team_name},
            {"$set": {"avg_ppg": avg}},
            upsert=True
        )

    champ_name, champ_ppg = predict_nba_champion()
    print(f"\nPredicted NBA Champion: {champ_name} ({champ_ppg} PPG)\n")

def predict_win_loss():
    all_teams = db['teams'].find()
    upcoming_games = get_upcoming_games()
    for team in all_teams:
        full_team_name = team['name']
        team_name = team['abbrev_name']

        for game in upcoming_games:
            if game['homeTeam'] == team_name or game['awayTeam'] == team_name:
                game_date = game['gameDateUTC'].strftime("%Y-%m-%d_%H-%M-%S")
                opponent = game['awayTeam'] if game['homeTeam'] == team_name else game['homeTeam']
                outcome = determine_win_loss(team_name, opponent, game_date)
                db['teams'].update_one(
                    {"name": full_team_name},
                    {"$set": {f"future_games.{game_date}.WinLoss": outcome}},
                    upsert=True
                )
                db['players'].update_many(
                    {
                        "team": team_name,
                        f"future_games.{game_date}": {"$exists": True}
                    },
                    {"$set": {f"future_games.{game_date}.WinLoss": outcome}},
                    upsert=True
                )
        print("Predicted W/L for:" + team_name)

def get_seasons():
    """
    Fetch all seasons from the NBA API and return them as a list.
    """
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
        print(games)

def upload_to_mongodb():
    # Call get_player_data and get_team_data, but data will be uploaded to MongoDB in the functions
    store_feedback() # Uncomment if you want to run feedback loop
    get_player_data()
    get_team_data()
    evaluate_feedback_discrepancies() # Uncomment if you want to run feedback loop
    make_future_predictions()
    predict_win_loss()
    #get_seasons()
    

if __name__ == "__main__":
    upload_to_mongodb()
 