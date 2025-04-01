from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import players, teams
import json
from datetime import datetime
from time import sleep

def get_player_data():
    all_players = players.get_players()
    players_json = {}

    for player in all_players:
        player_name = player['full_name']
        player_entry = {
            "name": player_name,
            "team": None,
            "games": {}
        }

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

            if not date or not isinstance(date, str):
                print(f"Skipping game with invalid date: {date}")
                continue
            formatted_date = date.replace('/', '-').replace(' ', '_')

            player_data = {
                "Season_ID": game["SEASON_ID"],
                "Game_ID": game["GAME_ID"],
                "Game_Date": game["GAME_DATE"],
                "Team_ID": game["TEAM_ID"],
                "Team": game["TEAM_ABBREVIATION"],
                "Team_Name": game["TEAM_NAME"],
                "Matchup": game["MATCHUP"],
                "WinLoss": game["WL"],
                "Minutes": game["MIN"],
                "Points": game["PTS"],
                "FG_Made": game["FGM"],
                "FG_Attempted": game["FGA"],
                "FG_Percentage": game["FG_PCT"],
                "3PT_Made": game["FG3M"],
                "3PT_Attempted": game["FG3A"],
                "3PT_Percentage": game["FG3_PCT"],
                "FT_Made": game["FTM"],
                "FT_Attempted": game["FTA"],
                "FT_Percentage": game["FT_PCT"],
                "Offensive_Rebounds": game["OREB"],
                "Defensive_Rebounds": game["DREB"],
                "Total_Rebounds": game["REB"],
                "Assists": game["AST"],
                "Steals": game["STL"],
                "Blocks": game["BLK"],
                "Turnovers": game["TOV"],
                "Personal_Fouls": game["PF"],
                "PlusMinus": game["PLUS_MINUS"],
                "is_future_game": False
            }


            player_entry["games"][formatted_date] = player_data

        player_entry["team"] = current_team
        players_json[player_name] = player_entry

        sleep(0.5)
        print("Finished stats for player " + player['full_name'])

    # Save to JSON file
    with open("players_data.json", "w") as f:
        json.dump(players_json, f, indent=4)
    print("Saved players data to players_data.json")


def get_team_data():
    all_teams = teams.get_teams()
    teams_json = {}

    for team in all_teams:
        team_name = team['full_name']
        team_entry = {
            "name": team_name,
            "abbrev_name": None,
            "games": {}
        }

        try:
            game_finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team['id'], timeout=3, date_from_nullable="09/30/2009")
        except:
            print("Skip: " + team_name)
            continue

        games = game_finder.get_data_frames()[0]

        for _, game in games.iterrows():
            date = game['GAME_DATE']

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

            team_entry["games"][formatted_date] = team_data
            team_entry["abbrev_name"] = game['TEAM_ABBREVIATION']

        teams_json[team_name] = team_entry

        sleep(0.5)
        print("Finished stats for team " + team['full_name'])

    # Save to JSON file
    with open("teams_data.json", "w") as f:
        json.dump(teams_json, f, indent=4)
    print("Saved teams data to teams_data.json")

if __name__ == "__main__":
    get_player_data()
    get_team_data()
