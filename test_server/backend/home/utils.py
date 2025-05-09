import datetime

# Team divisions mapping
team_divisions = {
    "NYK": "Atlantic",
    "BKN": "Atlantic",
    "BOS": "Atlantic",
    "PHI": "Atlantic",
    "TOR": "Atlantic",
    "NJN": "Atlantic",
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
    "NOH": "Southwest",
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

alias_abbreviations = {
    "NJN": "BKN",  # New Jersey Nets to Brooklyn Nets
    "NOH": "NOP",  # New Orleans Hornets to New Orleans Pelicans
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

def get_season_type_from_season_id(season_id):
    """
    Extract season type from SEASON_ID.
    Examples:
    - "22024" (first digit 2) → "Regular Season"
    - "42024" (first digit 4) → "Playoffs"
    - "52024" (first digit 5) → "Play-In Tournament"
    - "62024" (first digit 6) → "NBA Cup Finals"
    """
    if not season_id or not isinstance(season_id, str):
        return None
    
    try:
        first_digit = season_id[0]
        if first_digit == '1':
            return "Preseason"
        if first_digit == '2':
            return "Regular Season"
        elif first_digit == '4':
            return "Postseason" 
        elif first_digit == '5':
            return "Play-In Tournament"
        elif first_digit == '6':
            return "NBA Cup Finals"
        else:
            return None
    except IndexError:
        return None

def get_season_year_from_season_id(season_id):
    """
    Extract season year from SEASON_ID.
    Example: "22024" → "2024-25"
    """
    if not season_id or not isinstance(season_id, str):
        return None
    
    try:
        # Extract year portion (all digits after the first)
        year = int(season_id[1:])
        # Format as "YYYY-YY"
        return f"{year}-{(year % 100) + 1}"
    except (ValueError, IndexError):
        return None

def is_interconference_game(team_abbr, opponent_abbr):
    """
    Determine if a game is interconference (East vs West)
    """
    if team_abbr not in team_conferences or opponent_abbr not in team_conferences:
        return None
    
    return team_conferences[team_abbr] != team_conferences[opponent_abbr]

# FR26, FR27, FR28 - This function applies filters to game data
def apply_filters_to_games(games, filters):
    """
    Apply various filters to a list of games

    FR26, FR27, FR28 - Implements the core filtering logic for statistics
    """
    filtered_games = games.copy()
    
    # FR26, FR27 - Date range filters
    if 'date_from' in filters:
        try:
            date_from = datetime.datetime.strptime(filters['date_from'], '%Y-%m-%d')
            filtered_games = [
                game for game in filtered_games 
                if datetime.datetime.strptime(game['date'].split('_')[0], '%Y-%m-%d') >= date_from
            ]
        except ValueError:
            pass
    
    # FR26, FR27 - Month filter
    if 'date_to' in filters:
        try:
            date_to = datetime.datetime.strptime(filters['date_to'], '%Y-%m-%d')
            filtered_games = [
                game for game in filtered_games 
                if datetime.datetime.strptime(game['date'].split('_')[0], '%Y-%m-%d') <= date_to
            ]
        except ValueError:
            pass

    # FR26, FR27 - Season filter (e.g., "2022-23")
    if 'month' in filters and filters['month']:
        month = int(filters['month'])
        filtered_games = [
            game for game in filtered_games 
            if datetime.datetime.strptime(game['date'].split('_')[0], '%Y-%m-%d').month == month
        ]

    # FR26, FR27 - Season type filter (Regular Season, Postseason)
    if 'season' in filters and filters['season']:
        season = filters['season']
        filtered_games = [
            game for game in filtered_games 
            if get_season_year_from_season_id(game.get('SEASON_ID')) == season
        ]

    # FR26, FR27 - Game outcome filter (Win/Loss)
    if 'season_type' in filters and filters['season_type']:
        season_type = filters['season_type']
        filtered_games = [
            game for game in filtered_games 
            if get_season_type_from_season_id(game.get('SEASON_ID')) == season_type
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
    
    # FR26, FR27 - Division filter
    if 'division' in filters and filters['division']:
        division = filters['division']
        filtered_games = [
            game for game in filtered_games 
            if game.get('opponent_division') == division
        ]
    
    # FR26, FR27 - Conference filter
    if 'conference' in filters and filters['conference']:
        conference = filters['conference']
        filtered_games = [
            game for game in filtered_games 
            if game.get('opponent_conference') == conference
        ]
    
    # FR26, FR27 - Game type filter (Interconference/Intraconference)
    if 'game_type' in filters and filters['game_type'] and filters['game_type'] != 'All':
        is_inter = filters['game_type'] == 'Interconference'
        filtered_games = [
            game for game in filtered_games 
            if game.get('is_interconference', None) is not None and game.get('is_interconference') == is_inter
        ]
    
    # FR26, FR27 - Opponents filter (comma-separated list of team names)
    if 'opponents' in filters and filters['opponents']:
        opponent_names = filters['opponents'].split(',')
        opponent_abbrs = [team_abbr_map.get(name.strip(), '') for name in opponent_names]
        filtered_games = [
            game for game in filtered_games 
            if game.get('opponent_abbr', '') in opponent_abbrs
        ]
    
    # FR26, FR27 - Last N games filter
    if 'last_n_games' in filters and filters['last_n_games']:
        try:
            n = int(filters['last_n_games'])
            # Sort games by date (newest first) and take only the first n
            filtered_games.sort(key=lambda x: x['date'], reverse=True)
            filtered_games = filtered_games[:n]
        except ValueError:
            pass
    
    # FR28 - If no filters are applied, return all games (reset functionality)
    return filtered_games