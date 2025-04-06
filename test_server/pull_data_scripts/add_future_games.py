import requests
from datetime import datetime, timezone, timedelta
import pytz
# from time import sleep (removed as it is unused)

def get_upcoming_games():
    """
    Fetch the upcoming NBA games from the provided URL and return games that are scheduled 
    at least 2 hours after the current time.
    """
    url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        utc = pytz.utc
        upcoming_games = []
        current_time = datetime.now(timezone.utc)
        two_hours_from_now = current_time + timedelta(hours=2)

        for game_date in data["leagueSchedule"]["gameDates"]:
            for game in game_date["games"]:
                game_date_utc = datetime.strptime(game["gameDateUTC"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                
                # Check if game is at least 2 hours in the future
                if game_date_utc >= two_hours_from_now:
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
        print(f"Found {len(upcoming_games)} upcoming games.")
        return upcoming_games

    except requests.exceptions.RequestException as e:
        print(f"Error fetching schedule: {e}")
        return []

get_upcoming_games()