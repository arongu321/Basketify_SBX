import datetime

# Team divisions mapping
team_divisions = {
    "NYK": "Atlantic",
    "BKN": "Atlantic",
    "BOS": "Atlantic",
    "PHI": "Atlantic",
    "TOR": "Atlantic",
    "CHI": "Central",
    "CLE": "Central",
    "DET": "Central",
    "IND": "Central",
    "MIL": "Central",
    "ATL": "Southeast",
    "CHA": "Southeast",
    "MIA": "Southeast",
    "ORL": "Southeast",
    "WAS": "Southeast",
    "DAL": "Southwest",
    "HOU": "Southwest",
    "MEM": "Southwest",
    "NOP": "Southwest",
    "SAS": "Southwest",
    "DEN": "Northwest",
    "MIN": "Northwest",
    "OKC": "Northwest",
    "POR": "Northwest",
    "UTA": "Northwest",
    "GSW": "Pacific",
    "LAC": "Pacific",
    "LAL": "Pacific",
    "PHX": "Pacific",
    "SAC": "Pacific",
}

# Team conferences mapping
team_conferences = {
    "NYK": "East",
    "BKN": "East",
    "BOS": "East",
    "PHI": "East",
    "TOR": "East",
    "CHI": "East",
    "CLE": "East",
    "DET": "East",
    "IND": "East",
    "MIL": "East",
    "ATL": "East",
    "CHA": "East",
    "MIA": "East",
    "ORL": "East",
    "WAS": "East",
    "DAL": "West",
    "HOU": "West",
    "MEM": "West",
    "NOP": "West",
    "SAS": "West",
    "DEN": "West",
    "MIN": "West",
    "OKC": "West",
    "POR": "West",
    "UTA": "West",
    "GSW": "West",
    "LAC": "West",
    "LAL": "West",
    "PHX": "West",
    "SAC": "West"
}

# Helper to convert full team names to abbreviations
team_abbr_map = {
    "New York Knicks": "NYK",
    "Brooklyn Nets": "BKN",
    "Boston Celtics": "BOS",
    "Philadelphia 76ers": "PHI",
    "Toronto Raptors": "TOR",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Detroit Pistons": "DET",
    "Indiana Pacers": "IND",
    "Milwaukee Bucks": "MIL",
    "Atlanta Hawks": "ATL",
    "Charlotte Hornets": "CHA",
    "Miami Heat": "MIA",
    "Orlando Magic": "ORL",
    "Washington Wizards": "WAS",
    "Dallas Mavericks": "DAL",
    "Houston Rockets": "HOU",
    "Memphis Grizzlies": "MEM",
    "New Orleans Pelicans": "NOP",
    "San Antonio Spurs": "SAS",
    "Denver Nuggets": "DEN",
    "Minnesota Timberwolves": "MIN",
    "Oklahoma City Thunder": "OKC",
    "Portland Trail Blazers": "POR",
    "Utah Jazz": "UTA",
    "Golden State Warriors": "GSW",
    "Los Angeles Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Phoenix Suns": "PHX",
    "Sacramento Kings": "SAC"
}

def get_game_location(matchup):
    """
    Determine if a game is home or away based on the matchup
    """
    if ' vs. ' in matchup:
        return 'home'
    elif ' @ ' in matchup:
        return 'away'
    else:
        return 'unknown'

def get_opponent_from_matchup(matchup, team_abbr):
    """
    Extract opponent abbreviation from matchup string
    """
    if ' vs. ' in matchup:
        teams = matchup.split(' vs. ')
        return teams[1] if teams[0] == team_abbr else teams[0]
    elif ' @ ' in matchup:
        teams = matchup.split(' @ ')
        return teams[1] if teams[0] == team_abbr else teams[0]
    else:
        return None

def determine_season_year(date_str):
    """
    Determine the NBA season based on the date (e.g. 2022-12-25 would be in the 2022-23 season)
    """
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        year = date_obj.year
        month = date_obj.month
        
        # If month is October through December, it's part of the season starting that year
        if month >= 10:
            return f"{year}-{str(year+1)[2:]}"
        # If month is January through June, it's part of the season that started the previous year
        else:
            return f"{year-1}-{str(year)[2:]}"
    except (ValueError, TypeError):
        # Handle cases where date_str is not a proper date string
        return None

def determine_season_type(date_str):
    """
    Determine season type (regular/playoffs) based on date
    A very basic implementation - assuming post-April 15 is playoffs in most seasons
    """
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        month = date_obj.month
        day = date_obj.day
        
        # Rough estimate: after April 15 is typically playoffs
        if (month == 4 and day > 15) or month > 4:
            return "Postseason"
        else:
            return "Regular Season"
    except (ValueError, TypeError):
        return "Regular Season"

def is_interconference_game(team_abbr, opponent_abbr):
    """
    Determine if a game is interconference (East vs West)
    """
    if team_abbr not in team_conferences or opponent_abbr not in team_conferences:
        return None
    
    return team_conferences[team_abbr] != team_conferences[opponent_abbr]

def apply_filters_to_games(games, filters):
    """
    Apply various filters to a list of games
    """
    filtered_games = games.copy()
    
    # Date range filters
    if 'date_from' in filters:
        try:
            date_from = datetime.datetime.strptime(filters['date_from'], '%Y-%m-%d')
            filtered_games = [
                game for game in filtered_games 
                if datetime.datetime.strptime(game['date'].split('_')[0], '%Y-%m-%d') >= date_from
            ]
        except ValueError:
            pass
    
    if 'date_to' in filters:
        try:
            date_to = datetime.datetime.strptime(filters['date_to'], '%Y-%m-%d')
            filtered_games = [
                game for game in filtered_games 
                if datetime.datetime.strptime(game['date'].split('_')[0], '%Y-%m-%d') <= date_to
            ]
        except ValueError:
            pass
    
    # Season filter (e.g., "2022-23")
    if 'season' in filters and filters['season']:
        season = filters['season']
        filtered_games = [
            game for game in filtered_games 
            if determine_season_year(game['date'].split('_')[0]) == season
        ]
    
    # Season type filter (Regular Season, Postseason)
    if 'season_type' in filters and filters['season_type']:
        season_type = filters['season_type']
        filtered_games = [
            game for game in filtered_games 
            if determine_season_type(game['date'].split('_')[0]) == season_type
        ]
    
    # Game outcome filter (Win/Loss)
    if 'outcome' in filters and filters['outcome'] and filters['outcome'] != 'All':
        outcome = 'W' if filters['outcome'] == 'Win' else 'L'
        filtered_games = [
            game for game in filtered_games 
            if game.get('WinLoss') == outcome
        ]
    
    # Process Matchup-based filters
    for game in filtered_games:
        # We need to ensure each game has matchup info to apply these filters
        if 'Matchup' not in game:
            continue
            
        matchup = game['Matchup']
        team_abbr = game.get('TEAM_ABBREVIATION', '')
        opponent_abbr = get_opponent_from_matchup(matchup, team_abbr)
        
        game['game_location'] = get_game_location(matchup)
        game['opponent_abbr'] = opponent_abbr
        
        if opponent_abbr in team_divisions:
            game['opponent_division'] = team_divisions[opponent_abbr]
        
        if opponent_abbr in team_conferences:
            game['opponent_conference'] = team_conferences[opponent_abbr]
        
        if team_abbr in team_conferences and opponent_abbr in team_conferences:
            game['is_interconference'] = is_interconference_game(team_abbr, opponent_abbr)
    
    # Division filter
    if 'division' in filters and filters['division']:
        division = filters['division']
        filtered_games = [
            game for game in filtered_games 
            if game.get('opponent_division') == division
        ]
    
    # Conference filter
    if 'conference' in filters and filters['conference']:
        conference = filters['conference']
        filtered_games = [
            game for game in filtered_games 
            if game.get('opponent_conference') == conference
        ]
    
    # Game type filter (Interconference/Intraconference)
    if 'game_type' in filters and filters['game_type'] and filters['game_type'] != 'All':
        is_inter = filters['game_type'] == 'Interconference'
        filtered_games = [
            game for game in filtered_games 
            if game.get('is_interconference', None) is not None and game.get('is_interconference') == is_inter
        ]
    
    # Opponents filter (comma-separated list of team names)
    if 'opponents' in filters and filters['opponents']:
        opponent_names = filters['opponents'].split(',')
        opponent_abbrs = [team_abbr_map.get(name.strip(), '') for name in opponent_names]
        filtered_games = [
            game for game in filtered_games 
            if game.get('opponent_abbr', '') in opponent_abbrs
        ]
    
    # Last N games filter
    if 'last_n_games' in filters and filters['last_n_games']:
        try:
            n = int(filters['last_n_games'])
            # Sort games by date (newest first) and take only the first n
            filtered_games.sort(key=lambda x: x['date'], reverse=True)
            filtered_games = filtered_games[:n]
        except ValueError:
            pass
    
    return filtered_games