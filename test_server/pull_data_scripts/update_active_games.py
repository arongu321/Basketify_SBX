import json
import os
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import leaguegamefinder, commonplayerinfo
from datetime import datetime
from time import sleep

# Path to the players_data.json file
DATA_FILE = 'players_data.json'
TEAM_FILE = 'teams_data.json'
active_players = set([player['id'] for player in players.get_active_players()])

active_teams = set([team['id'] for team in teams.get_teams()])
def is_valid_game(game):
    # --- Filter by season ---
    if str(game['SEASON_ID']).startswith("1"):
        return False
    
    # --- Filter by date ---
    date_str = game['GAME_DATE']  # e.g., '2020-07-15'
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month = date_obj.month
    year = date_obj.year

    # Allowed bubble months & COVID special case
    allowed_special_cases = [
        (7, 2020),
        (8, 2020),
        (9, 2020),
        (10, 2020),
        (7, 2021)
    ]

    if (month in [7,8,9] and (month, year) not in allowed_special_cases):
        return False
    
    return True

def load_data(file_path):
    """Load data from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def save_data(file_path, data):
    """Save updated data to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def update_active_team_games(data, active_teams):
    """Update games for active teams."""
    for team_id, team_info in data.items():
        game_finder = None
        print(f"Checking team {team_id}...")
        if int(team_id) not in active_teams:
            print(f"Team {team_id} is not active.")
        else:
            while game_finder is None:
                try:
                    game_finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id, timeout=5)
                    game_finder_df = game_finder.get_data_frames()[0]
                    games = game_finder_df.to_dict(orient='records')
                except:
                    print(f"Skipped game finder: {team_id}")
                    sleep(2)
            team_info['games'] = []
            for game in games:
                if is_valid_game(game):
                    team_info['games'].append(game)
            print(f"Finished Team {team_id}")
            sleep(1)
    return data

def update_active_players_games(data, active_players):
    """Update games for active players."""
    for player_id, player_info in data.items():
        game_finder = None
        print(f"Checking player {player_id}...")
        if int(player_id) not in active_players:
            print(f"Player {player_id} is not active.")
        else:
            while game_finder is None:
                try:
                    game_finder = leaguegamefinder.LeagueGameFinder(player_id_nullable=player_id, timeout=5)
                    game_finder_df = game_finder.get_data_frames()[0]
                    games = game_finder_df.to_dict(orient='records')
                except:
                    print(f"Skipped game finder: {player_id}")
                    sleep(2)
            player_info['games'] = []
            for game in games:
                if is_valid_game(game):
                    player_info['games'].append(game)
            print(f"Finished Player {player_id}")
            sleep(1)
    return data
        
        

def main():
    try:
        # # Load the players data
        # players_data = load_data(DATA_FILE)
        
        # players_data = update_active_players_games(players_data, active_players)

        # save_data(DATA_FILE, players_data)

        # print("Successfully updated active players' games.")

        # Load the teams data
        teams_data = load_data(TEAM_FILE)

        teams_data = update_active_team_games(teams_data, active_teams)

        save_data(TEAM_FILE, teams_data)

        print("Successfully updated active teams' games.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()