from django.http import JsonResponse
import datetime
from pymongo import MongoClient


# global to prevent having to connect multiple times
mongo_client = None


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


def welcome(request):
    return JsonResponse({'message': 'Welcome to Django with React!'})


def get_login_message(request):
    now = datetime.datetime.now()
    message = f"Welcome to the Login Page! Current time from Django: {now}"
    return JsonResponse({"message": message})


def get_search_message(request):
    now = datetime.datetime.now()
    message = f"Welcome to the Login Page! Current time from Django: {now}"
    return JsonResponse({"message": message})


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
    

# Helper function to replace NaN with a default value
def sanitize_value(value):
    if isinstance(value, float) and (value != value):
        return 0
    return value


def get_player_stats(request, name):
    try:
        client = get_mongo_client()
        db = client['nba_stats']
        players_collection = db['players']
        
        player = players_collection.find_one({"name": name})
        
        if not player:
            return JsonResponse({'error': 'Player not found'}, status=404)
        
        # extract game stats from the player's data
        player_stats = []
        
        for game_date, game_data in player['games'].items():
            stats = {
                "date": sanitize_value(game_date),
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
                "turnovers": sanitize_value(game_data.get("Turnovers", 0))
            }
            player_stats.append(stats)
        
        return JsonResponse({"stats": player_stats}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_team_stats(request, name):
    try:
        client = get_mongo_client()
        db = client['nba_stats']
        teams_collection = db['teams']
        
        team = teams_collection.find_one({"name": name})
        
        if not team:
            return JsonResponse({'error': 'Team not found'}, status=404)
        
        # extract game stats from the team's data
        team_stats = []
        
        for game_date, game_data in team['games'].items():
            stats = {
                "date": sanitize_value(game_date),
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
                "turnovers": sanitize_value(game_data.get("Turnovers", 0))
            }
            team_stats.append(stats)
        
        return JsonResponse({"stats": team_stats}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
