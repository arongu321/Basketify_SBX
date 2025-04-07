from django.http import JsonResponse
import datetime
from pymongo import MongoClient
from .utils import apply_filters_to_games, determine_season_year, determine_season_type, get_game_location, get_opponent_from_matchup, alias_abbreviations


# global to prevent having to connect multiple times
mongo_client = None


# connect to MongoDB database, required for all data-related tasks (practically all FRs)
def get_mongo_client():
    global mongo_client
    # check if mongo client is already initialized
    if mongo_client is not None:
        return mongo_client
    
    # remote Atlas DB
    uri = "mongodb+srv://zschmidt:ECE493@basketifycluster.dr6oe.mongodb.net"

    try:
        mongo_client = MongoClient(uri)
    except:
        print("Couldn't connect to mongodb database at URI: " + uri)
        return None
    
    print("Successfully connected")
    return mongo_client


# used to asynchronously pre-fetch connection to MongoDB
def handle_load_db_request(request):
    get_mongo_client()
    return JsonResponse({'message': 'Connected to DB'})


# left for debugging purposes: frontend tests connection by this route
def welcome(request):
    return JsonResponse({'message': 'Welcome to Django with React!'})


# backend to query MongoDB for player name, returns all players where name partially
# matches. Fulfills FR7
def search_player(request):
    # get 'name' param from the GET request
    name = request.GET.get('name', None)

    if not name:
        return JsonResponse({'error': 'Name parameter is required'}, status=400)

    try:
        client = get_mongo_client()

        db = client['nba_stats_all']
        players_collection = db['players']

        matching_players = players_collection.find(
            {"name": {"$regex": name, "$options": "i"}}  # case-insensitive and allows substring match
        )

        player_data_list = []
        for player in matching_players:
            player_data_list.append({
                'name': player.get('name', ''),
            })

        if not player_data_list:
            return JsonResponse({'message': 'No players found'}, status=404)

        return JsonResponse({'players': player_data_list}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# backend to query MongoDB for team name, returns all team where name partially
# matches. Fulfills FR8
def search_team(request):
    # get 'name' param from the GET request
    name = request.GET.get('name', None)

    if not name:
        return JsonResponse({'error': 'Name parameter is required'}, status=400)

    try:
        client = get_mongo_client()

        db = client['nba_stats_all']
        teams_collection = db['teams']

        matching_teams = teams_collection.find(
            {"name": {"$regex": name, "$options": "i"}}  # case-insensitive and allows substring match
        )

        team_data_list = []
        for team in matching_teams:
            team_data_list.append({
                'name': team.get('name', ''),
                'location': team.get('location', '')
            })

        if not team_data_list:
            return JsonResponse({'message': 'No teams found'}, status=404)
        
        return JsonResponse({'teams': team_data_list}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# helper function to replace NaN with a default value, used in get_player_stats and get_team_stats.
# Contributes to fulfilling FR9, FR11
def sanitize_value(value):
    if isinstance(value, float) and (value != value):
        return 0
    return value


# helper function to extract season based on yyy-mm-dd string (e.g. 2025-03-12 falls in '2024-2025' season).
# Contributes to fulfilling FR10, FR15
def get_season_from_date(date_str):
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        year = date_obj.year
        month = date_obj.month
        
        # if month is October or later, season starts in current year
        if month >= 10:
            return f"{year}-{year + 1}"
        # otherwise, season started in previous year
        else:
            return f"{year - 1}-{year}"
    except ValueError:
        return None


# groups game-by-game data into seasons. Contributes to fulfilling FR10, FR15
def aggregate_seasonal_stats(stats):
    grouped_by_season = {}
    
    for stat in stats:
        season = get_season_from_date(stat['date'])
        if not season:
            continue
            
        if season not in grouped_by_season:
            grouped_by_season[season] = {
                'season': season,
                'points': 0,
                'rebounds': 0,
                'assists': 0,
                'fieldGoalsMade': 0,
                'fieldGoalsAttempted': 0,
                'fieldGoalPercentage': 0,
                'threePointsMade': 0,
                'threePointsAttempted': 0,
                'threePointPercentage': 0,
                'freeThrowsMade': 0,
                'freeThrowsAttempted': 0,
                'freeThrowPercentage': 0,
                'steals': 0,
                'blocks': 0,
                'turnovers': 0,
                'gamesPlayed': 0
            }
            
        # aggregate game-by-game stats into seasons
        season_stats = grouped_by_season[season]
        season_stats['points'] += stat.get('points', 0) or 0
        season_stats['rebounds'] += stat.get('rebounds', 0) or 0
        season_stats['assists'] += stat.get('assists', 0) or 0
        season_stats['fieldGoalsMade'] += stat.get('fieldGoalsMade', 0) or 0
        season_stats['threePointsMade'] += stat.get('threePointsMade', 0) or 0
        season_stats['freeThrowsMade'] += stat.get('freeThrowsMade', 0) or 0
        season_stats['steals'] += stat.get('steals', 0) or 0
        season_stats['blocks'] += stat.get('blocks', 0) or 0
        season_stats['turnovers'] += stat.get('turnovers', 0) or 0
        season_stats['gamesPlayed'] += 1

        #calculate attempts based on made and percent (required to get seasonal percentage)
        if stat.get('fieldGoalPercentage', 0) > 0:
            attempts = stat.get('fieldGoalsMade', 0) / stat.get('fieldGoalPercentage', 0)
            season_stats['fieldGoalsAttempted'] += attempts
        if stat.get('threePointPercentage', 0) > 0:
            attempts = stat.get('threePointsMade', 0) / stat.get('threePointPercentage', 0)
            season_stats['threePointsAttempted'] += attempts
        if stat.get('freeThrowPercentage', 0) > 0:
            attempts = stat.get('freeThrowsMade', 0) / stat.get('freeThrowPercentage', 0)
            season_stats['freeThrowsAttempted'] += attempts

    # percentage = total season made / total season attempts
    for season, stats in grouped_by_season.items():
        if stats['fieldGoalsAttempted'] > 0:
            stats['fieldGoalPercentage'] = stats['fieldGoalsMade'] / stats['fieldGoalsAttempted']
        if stats['threePointsAttempted'] > 0:
            stats['threePointPercentage'] = stats['threePointsMade'] / stats['threePointsAttempted']
        if stats['freeThrowsAttempted'] > 0:
            stats['freeThrowPercentage'] = stats['freeThrowsMade'] / stats['freeThrowsAttempted']

    return list(grouped_by_season.values())


# main backend route which receieves an HTTP request with a player name and returns
# the game-by-game and aggregated seasonal stats for that player. Fulfills FR9, FR10, FR11, FR15
def get_player_stats(request, name):
    """
    Get player stats with various filtering options
    """
    try:
        client = get_mongo_client()
        db = client['nba_stats_all']
        players_collection = db['players']
        
        player = players_collection.find_one({"name": name})
        
        if not player:
            return JsonResponse({'error': 'Player not found'}, status=404)
        
        # Extract filter parameters from request
        filters = {}
        for param in ['date_from', 'date_to', 'last_n_games', 'season', 'season_type', 
                     'division', 'conference', 'game_type', 'outcome', 'opponents']:
            if request.GET.get(param):
                filters[param] = request.GET.get(param)
        
        player_stats = []
        
        # Combine past and future games
        all_games = {**player.get('games', {}), **player.get('future_games', {})}
        
        for game_date, game_data in all_games.items():
            # Skip if we're missing core data for filtering
            if not game_date or not isinstance(game_date, str):
                continue
                
            # Extract date part if the format is YYYY-MM-DD_HH-MM-SS
            date_parts = game_date.split('_')
            date_only = date_parts[0] if len(date_parts) > 0 else game_date
            
            # Extract opponent from matchup using our utility function
            opponent = ""
            if "Matchup" in game_data:
                matchup = game_data["Matchup"]
                team_abbr = game_data.get("Team", "")
                opponent = get_opponent_from_matchup(matchup, team_abbr)
                if opponent in alias_abbreviations:
                    opponent = alias_abbreviations[opponent]
            
            # Basic stats model
            stats = {
                "date": date_only,
                "opponent": opponent,  # Add opponent info
                "points": sanitize_value(game_data.get("Points", 0)),
                "rebounds": sanitize_value(game_data.get("scoredRebounds", 0)),
                "assists": sanitize_value(game_data.get("Assists", 0)),
                "fieldGoalsMade": sanitize_value(game_data.get("FG_scored", 0)),
                "fieldGoalPercentage": sanitize_value(game_data.get("FG_pctg", 0)),
                "threePointsMade": sanitize_value(game_data.get("3_pts_scored", 0)),
                "threePointPercentage": sanitize_value(game_data.get("3_pts_pctg", 0)),
                "freeThrowsMade": sanitize_value(game_data.get("FT_made", 0)),
                "freeThrowPercentage": sanitize_value(game_data.get("FT_pctg", 0)),
                "steals": sanitize_value(game_data.get("Steals", 0)),
                "blocks": sanitize_value(game_data.get("Blocks", 0)),
                "turnovers": sanitize_value(game_data.get("Turnovers", 0)),
                "is_future_game": game_data.get('is_future_game', 0),
                # Include additional fields needed for filtering
                "Matchup": game_data.get("Matchup", ""),
                "TEAM_ABBREVIATION": game_data.get("Team", ""),
                "WinLoss": game_data.get("WinLoss", "")
            }
            player_stats.append(stats)
        
        # Apply filters
        filtered_stats = apply_filters_to_games(player_stats, filters)
        
        # Sort games by date (oldest first for statistics calculation)
        filtered_stats.sort(key=lambda x: x['date'])
        
        # Generate seasonal stats from the filtered game stats
        seasonal_stats = aggregate_seasonal_stats(filtered_stats)
        
        # Remove temporary fields used for filtering before returning
        for game in filtered_stats:
            fields_to_remove = ['Matchup', 'TEAM_ABBREVIATION', 'game_location', 
                              'opponent_abbr', 'opponent_division', 'opponent_conference', 
                              'is_interconference']
            for field in fields_to_remove:
                if field in game and field != 'opponent':  # Keep the opponent field
                    del game[field]
        
        return JsonResponse({
            "stats": filtered_stats,
            "seasonal_stats": seasonal_stats
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# main backend route which receieves an HTTP request with a team name and returns
# the game-by-game and aggregated seasonal stats for that team. Fulfills FR9, FR10, FR11, FR15
def get_team_stats(request, name):
    """
    Get team stats with various filtering options
    """
    try:
        client = get_mongo_client()
        db = client['nba_stats_all']
        teams_collection = db['teams']
        
        team = teams_collection.find_one({"name": name})
        
        if not team:
            return JsonResponse({'error': 'Team not found'}, status=404)
        
        # Extract filter parameters from request
        filters = {}
        for param in ['date_from', 'date_to', 'last_n_games', 'season', 'season_type', 
                     'division', 'conference', 'game_type', 'outcome', 'opponents']:
            if request.GET.get(param):
                filters[param] = request.GET.get(param)
        
        team_stats = []
        
        # Combine past and future games
        all_games = {**team.get('games', {}), **team.get('future_games', {})}
        team_abbr = team.get('abbrev_name', '')
        
        for game_date, game_data in all_games.items():
            # Skip if we're missing core data for filtering
            if not game_date or not isinstance(game_date, str):
                continue
                
            # Extract date part if the format is YYYY-MM-DD_HH-MM-SS
            date_parts = game_date.split('_')
            date_only = date_parts[0] if len(date_parts) > 0 else game_date
            
            # Extract opponent from matchup using our utility function
            opponent = ""
            if "Matchup" in game_data:
                matchup = game_data["Matchup"]
                opponent = get_opponent_from_matchup(matchup, team_abbr)
                if opponent in alias_abbreviations:
                    opponent = alias_abbreviations[opponent]
            
            # Basic stats model
            stats = {
                "date": date_only,
                "opponent": opponent,  # Add opponent info
                "points": sanitize_value(game_data.get("Points", 0)),
                "rebounds": sanitize_value(game_data.get("scoredRebounds", 0)),
                "assists": sanitize_value(game_data.get("Assists", 0)),
                "fieldGoalsMade": sanitize_value(game_data.get("FG_scored", 0)),
                "fieldGoalPercentage": sanitize_value(game_data.get("FG_pctg", 0)),
                "threePointsMade": sanitize_value(game_data.get("3_pts_scored", 0)),
                "threePointPercentage": sanitize_value(game_data.get("3_pts_pctg", 0)),
                "freeThrowsMade": sanitize_value(game_data.get("FT_made", 0)),
                "freeThrowPercentage": sanitize_value(game_data.get("FT_pctg", 0)),
                "steals": sanitize_value(game_data.get("Steals", 0)),
                "blocks": sanitize_value(game_data.get("Blocks", 0)),
                "turnovers": sanitize_value(game_data.get("Turnovers", 0)),
                "is_future_game": game_data.get('is_future_game', 0),
                # Include additional fields needed for filtering
                "Matchup": game_data.get("Matchup", ""),
                "TEAM_ABBREVIATION": team_abbr,
                "WinLoss": game_data.get("WinLoss", "")
            }
            team_stats.append(stats)
        
        # Apply filters
        filtered_stats = apply_filters_to_games(team_stats, filters)
        
        # Sort games by date (oldest first for statistics calculation)
        filtered_stats.sort(key=lambda x: x['date'])
        
        # Generate seasonal stats from the filtered game stats
        seasonal_stats = aggregate_seasonal_stats(filtered_stats)
        
        # Remove temporary fields used for filtering before returning
        for game in filtered_stats:
            fields_to_remove = ['Matchup', 'TEAM_ABBREVIATION', 'game_location', 
                              'opponent_abbr', 'opponent_division', 'opponent_conference', 
                              'is_interconference']
            for field in fields_to_remove:
                if field in game and field != 'opponent':  # Keep the opponent field
                    del game[field]
        
        return JsonResponse({
            "stats": filtered_stats,
            "seasonal_stats": seasonal_stats
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def predict_nba_champion(request):
    client = get_mongo_client()
    db = client['nba_stats_all']
    teams_col = db["teams"]

    top_team = teams_col.find_one(
        {"avg_ppg": {"$exists": True}},
        sort=[("avg_ppg", -1)]
    )
    if top_team:
        return JsonResponse({
            "top_team": top_team["name"], 
            "top_team_ppg": top_team["avg_ppg"]
        }, status=200)
    return JsonResponse({'error': "No team has avg_ppg recorded"}, status=500)
