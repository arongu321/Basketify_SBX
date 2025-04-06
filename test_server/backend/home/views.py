from django.http import JsonResponse
import datetime
from pymongo import MongoClient


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


def get_ml_predictions_msg(request):
    now = datetime.datetime.now()
    message = f"Welcome to the ML Predictions Page! Current time from Django: {now}"
    return JsonResponse({"message": message})


# backend to query MongoDB for player name, returns all players where name partially
# matches. Fulfills FR7
def search_player(request):
    # get 'name' param from the GET request
    name = request.GET.get('name', None)

    if not name:
        return JsonResponse({'error': 'Name parameter is required'}, status=400)

    try:
        client = get_mongo_client()

        db = client['nba_stats']
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

        db = client['nba_stats']
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
    try:
        client = get_mongo_client()
        db = client['nba_stats']
        players_collection = db['players']
        
        player = players_collection.find_one({"name": name})
        
        if not player:
            return JsonResponse({'error': 'Player not found'}, status=404)

        # parse filter params from request
        date_from = request.GET.get('date_from', None)
        date_to = request.GET.get('date_to', None)
        last_n_games = request.GET.get('last_n_games', None)
        
        player_stats = []

        # combine past and future game
        all_games = {**player.get('games', {}), **player.get('future_games', {})}
        
        for game_date, game_data in all_games.items():
            # apply date filters if specified
            if date_from or date_to:
                try:
                    # extract the date part if the format is YYYY-MM-DD_HH-MM-SS
                    date_parts = game_date.split('_')
                    date_only = date_parts[0] if len(date_parts) > 0 else game_date
                    
                    # check if the date is in valid format
                    game_date_obj = datetime.datetime.strptime(date_only, '%Y-%m-%d')
                    
                    if date_from:
                        date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d')
                        if game_date_obj < date_from_obj:
                            continue
                            
                    if date_to:
                        date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d')
                        if game_date_obj > date_to_obj:
                            continue
                except (ValueError, IndexError):
                    # skip games with invalid date format
                    print(f"Skipping game with invalid date format: {game_date}")
                    continue
            
            date_parts = game_date.split('_')
            game_date = date_parts[0] if len(date_parts) > 0 else game_date
            stats = {
                "date": sanitize_value(game_date),
                "date_obj": datetime.datetime.strptime(game_date.split('_')[0], '%Y-%m-%d') if '_' in game_date else None,
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
                "is_future_game": game_data.get('is_future_game', 0)
            }
            player_stats.append(stats)
        
        # apply the "Last N Games" filter if specified (excluding future games)
        if last_n_games:
            try:
                n = int(last_n_games)
                # create a list of past games (non-future games)
                past_games = [game for game in player_stats if not game.get('is_future_game', False)]
                
                # sort games by date (handling cases where date_obj might be None)
                def get_date_for_sorting(game):
                    if game.get('date_obj') is not None:
                        return game['date_obj']
                    # fallback is to try to parse the date directly
                    try:
                        date_str = game['date'].split('_')[0] if '_' in game['date'] else game['date']
                        return datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    except (ValueError, AttributeError):
                        # if parsing fails, return a very old date to sort to the end
                        return datetime.datetime(1900, 1, 1)
                
                past_games.sort(key=get_date_for_sorting, reverse=True)
                
                # take only the first N games
                filtered_past_games = past_games[:n]
                
                # add future games (they're not affected by Last N Games filter)
                future_games = [game for game in player_stats if game.get('is_future_game', False)]
                
                # replace player_stats with the filtered list
                player_stats = filtered_past_games + future_games
            except (ValueError, TypeError) as e:
                print(f"Invalid last_n_games parameter: {last_n_games}, Error: {e}")
                # just continue without applying this filter if there's an error
        
        # remove temporary date_obj used for sorting
        for game in player_stats:
            if 'date_obj' in game:
                del game['date_obj']
        
        # generate seasonal stats from the filtered game stats
        seasonal_stats = aggregate_seasonal_stats(player_stats)
        
        return JsonResponse({
            "stats": player_stats,
            "seasonal_stats": seasonal_stats
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# main backend route which receieves an HTTP request with a team name and returns
# the game-by-game and aggregated seasonal stats for that team. Fulfills FR9, FR10, FR11, FR15
def get_team_stats(request, name):
    try:
        client = get_mongo_client()
        db = client['nba_stats']
        teams_collection = db['teams']
        
        team = teams_collection.find_one({"name": name})
        
        if not team:
            return JsonResponse({'error': 'Team not found'}, status=404)
        
        # parse filter parameters from request
        date_from = request.GET.get('date_from', None)
        date_to = request.GET.get('date_to', None)
        last_n_games = request.GET.get('last_n_games', None)
        
        team_stats = []

        all_games = {**team.get('games', {}), **team.get('future_games', {})}
        
        for game_date, game_data in all_games.items():
            # apply date filters if specified
            if date_from or date_to:
                try:
                    # extract the date part if the format is YYYY-MM-DD_HH-MM-SS
                    date_parts = game_date.split('_')
                    date_only = date_parts[0] if len(date_parts) > 0 else game_date
                    
                    # check if the date is in valid format
                    game_date_obj = datetime.datetime.strptime(date_only, '%Y-%m-%d')
                    
                    if date_from:
                        date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d')
                        if game_date_obj < date_from_obj:
                            continue
                            
                    if date_to:
                        date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d')
                        if game_date_obj > date_to_obj:
                            continue
                except (ValueError, IndexError):
                    # skip games with invalid date format
                    print(f"Skipping game with invalid date format: {game_date}")
                    continue
            
            date_parts = game_date.split('_')
            game_date = date_parts[0] if len(date_parts) > 0 else game_date
            stats = {
                "date": sanitize_value(game_date),
                "date_obj": datetime.datetime.strptime(game_date.split('_')[0], '%Y-%m-%d') if '_' in game_date else None,
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
                "is_future_game": game_data.get('is_future_game', 0)
            }
            team_stats.append(stats)
        
        # apply the "Last N Games" filter if specified (excluding future games)
        if last_n_games:
            try:
                n = int(last_n_games)
                # create a list of past games (non-future games)
                past_games = [game for game in team_stats if not game.get('is_future_game', False)]
                
                # sort games by date (handling cases where date_obj might be None)
                def get_date_for_sorting(game):
                    if game.get('date_obj') is not None:
                        return game['date_obj']
                    # fallback: Try to parse the date directly
                    try:
                        date_str = game['date'].split('_')[0] if '_' in game['date'] else game['date']
                        return datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    except (ValueError, AttributeError):
                        # if parsing fails, return a very old date to sort to the end
                        return datetime.datetime(1900, 1, 1)
                
                past_games.sort(key=get_date_for_sorting, reverse=True)
                
                # take only the first N games
                filtered_past_games = past_games[:n]
                
                # add future games (they're not affected by Last N Games filter)
                future_games = [game for game in team_stats if game.get('is_future_game', False)]
                
                # replace player_stats with the filtered list
                team_stats = filtered_past_games + future_games
            except (ValueError, TypeError) as e:
                print(f"Invalid last_n_games parameter: {last_n_games}, Error: {e}")
                # just continue without applying this filter if there's an error
        
        # remove temporary date_obj used for sorting
        for game in team_stats:
            if 'date_obj' in game:
                del game['date_obj']
        
        # generate seasonal stats from the filtered game stats
        seasonal_stats = aggregate_seasonal_stats(team_stats)
        
        return JsonResponse({
            "stats": team_stats,
            "seasonal_stats": seasonal_stats
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    