from django.http import JsonResponse
import datetime
from pymongo import MongoClient


# Global variable to store MongoDB client
mongo_client = None


def get_mongo_client():
    global mongo_client
    # Check if the MongoDB client is already initialized
    if mongo_client is not None:
        return mongo_client
    
    # MongoDB Atlas URI
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
    # get 'name' parameter from the GET request
    name = request.GET.get('name', None)

    if not name:
        return JsonResponse({'error': 'Name parameter is required'}, status=400)

    try:
        client = get_mongo_client()

        db = client['nba_stats']
        players_collection = db['players']

        # '$regex' used for case-insensitive matching of player names
        matching_players = players_collection.find(
            {"name": {"$regex": name, "$options": "i"}}
        )

        player_data_list = []
        for player in matching_players:
            player_data_list.append({
                'name': player.get('name', ''),
            })

        if not player_data_list:
            return JsonResponse({'message': 'No players found'}, status=404)

        # good return
        return JsonResponse({'players': player_data_list}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def search_team(request):
    # Get the 'name' parameter from the GET request
    name = request.GET.get('name', None)

    if not name:
        return JsonResponse({'error': 'Name parameter is required'}, status=400)

    # test data for now
    team_data_list = []
    team_data_list.append({
        'name': "Lakers",
        'location': "LA"
    })
    team_data_list.append({
        'name': "Warriors",
        'location': "San Francisco"
    })

    return JsonResponse({'teams': team_data_list}, status=200)


def get_player_stats(request, name):
    player_stats = {
        "test_player": [
            {"year": 2022, "points": 25, "rebounds": 5, "assists": 7, "fieldGoalsMade": 10, "fieldGoalPercentage": 50, "threePointsMade": 5, "threePointPercentage": 40, "freeThrowsMade": 8, "freeThrowPercentage": 80, "steals": 2, "blocks": 1, "turnovers": 3},
            {"year": 2021, "points": 22, "rebounds": 4, "assists": 6, "fieldGoalsMade": 9, "fieldGoalPercentage": 45, "threePointsMade": 4, "threePointPercentage": 35, "freeThrowsMade": 6, "freeThrowPercentage": 75, "steals": 1, "blocks": 1, "turnovers": 2}
        ]
    }
    return JsonResponse({"stats": player_stats["test_player"]}, status=200)

def get_team_stats(request, name):
    team_stats = {
        "test_team": [
            {"year": 2022, "points": 105, "rebounds": 48, "assists": 23, "fieldGoalsMade": 40, "fieldGoalPercentage": 45, "threePointsMade": 12, "threePointPercentage": 35, "freeThrowsMade": 18, "freeThrowPercentage": 75, "steals": 8, "blocks": 5, "turnovers": 12},
            {"year": 2021, "points": 100, "rebounds": 45, "assists": 22, "fieldGoalsMade": 38, "fieldGoalPercentage": 43, "threePointsMade": 10, "threePointPercentage": 30, "freeThrowsMade": 16, "freeThrowPercentage": 78, "steals": 7, "blocks": 4, "turnovers": 11}
        ]
    }
    return JsonResponse({"stats": team_stats["test_team"]}, status=200)
