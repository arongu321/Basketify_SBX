import json

team_abbr_to_id = {
    "ATL": "1610612737",  # Atlanta Hawks
    "BOS": "1610612738",  # Boston Celtics
    "CLE": "1610612739",  # Cleveland Cavaliers
    "NOP": "1610612740",  # New Orleans Pelicans/Hornets
    "CHI": "1610612741",  # Chicago Bulls
    "DAL": "1610612742",  # Dallas Mavericks
    "DEN": "1610612743",  # Denver Nuggets
    "GSW": "1610612744",  # Golden State Warriors
    "HOU": "1610612745",  # Houston Rockets
    "LAC": "1610612746",  # Los Angeles Clippers
    "LAL": "1610612747",  # Los Angeles Lakers
    "MIA": "1610612748",  # Miami Heat
    "MIL": "1610612749",  # Milwaukee Bucks
    "MIN": "1610612750",  # Minnesota Timberwolves
    "BKN": "1610612751",  # Brooklyn/New Jersey Nets
    "NYK": "1610612752",  # New York Knicks
    "ORL": "1610612753",  # Orlando Magic
    "IND": "1610612754",  # Indiana Pacers
    "PHI": "1610612755",  # Philadelphia 76ers
    "PHX": "1610612756",  # Phoenix Suns
    "POR": "1610612757",  # Portland Trail Blazers
    "SAC": "1610612758",  # Sacramento Kings
    "SAS": "1610612759",  # San Antonio Spurs
    "OKC": "1610612760",  # Oklahoma City Thunder/Seattle SuperSonics
    "TOR": "1610612761",  # Toronto Raptors
    "UTA": "1610612762",  # Utah Jazz
    "MEM": "1610612763",  # Vancouver/Memphis Grizzlies
    "WAS": "1610612764",  # Washington Wizards/Bullets
    "DET": "1610612765",  # Detroit Pistons
    "CHA": "1610612766",  # Charlotte Hornets/Bobcats
}

id_to_team_abbr = {v: k for k, v in team_abbr_to_id.items()}

defunct_team_abbr_to_id = {
    "SEA": "1610612760", # Seattle SuperSonics (now OKC Thunder)
    "VAN": "1610612763", # Vancouver Grizzlies (now Memphis Grizzlies)
    "NJN": "1610612751", # New Jersey Nets (now Brooklyn Nets)
    "NOH": "1610612740", # New Orleans Hornets (now New Orleans Pelicans)
    "NOK": "1610612740", # New Orleans/Oklahoma City Hornets (now New Orleans Pelicans)
    "KCK": "1610612758", # Kansas City Kings (now Sacramento Kings)
    "GOS": "1610612744", # Golden State Warriors (now Golden State Warriors)
    "SDC": "1610612746", # San Diego Clippers (now Los Angeles Clippers)
    "UTH": "1610612762", # Utah Jazz (now Utah Jazz)
    "CHH": "1610612766", # Charlotte Hornets (now Charlotte Hornets)
    "PHL": "1610612755", # Philadelphia 76ers (now Philadelphia 76ers)
    "SAN": "1610612759", # San Antonio Spurs (now San Antonio Spurs)
}

team_abbr_to_team_name = {
    "ATL": "Atlanta Hawks",
    "BOS": "Boston Celtics",
    "CLE": "Cleveland Cavaliers",
    "NOP": "New Orleans Pelicans",
    "CHI": "Chicago Bulls",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "LAC": "Los Angeles Clippers",
    "LAL": "Los Angeles Lakers",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "BKN": "Brooklyn Nets",
    "NYK": "New York Knicks",
    "ORL": "Orlando Magic",
    "IND": "Indiana Pacers",
    "PHI": "Philadelphia 76ers",
    "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "OKC": "Oklahoma City Thunder",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "MEM": "Memphis Grizzlies",
    "WAS": "Washington Wizards/Bullets", # Bullets(1963-1997) were rebranded to Wizards
    "DET": "Detroit Pistons",
    "CHA": "Charlotte Hornets/Bobcats", # Bobcats(2004-2013) were rebranded to Hornets
    "SEA": "Seattle SuperSonics",  # Defunct
    "VAN": "Vancouver Grizzlies",  # Defunct
    "NJN": "New Jersey Nets",     # Defunct
    "NOH": "New Orleans Hornets", # Defunct
    "NOK": "New Orleans/Oklahoma City Hornets", # Defunct
    "KCK": "Kansas City Kings",   # Defunct
    "GOS": "Golden State Warriors", # Defunct
    "UTH": "Utah Jazz", # Defunct
    "SDC": "San Diego Clippers",  # Defunct
    "CHH": "Charlotte Hornets", # Defunct
    "PHL": "Philadelphia 76ers", # Defunct
    "SAN": "San Antonio Spurs", # Defunct
}

# Team division and conference mappings
team_divisions = {
    # Eastern Conference
    "ATL": {"division": "Southeast", "conference": "East"},
    "BOS": {"division": "Atlantic", "conference": "East"},
    "BKN": {"division": "Atlantic", "conference": "East"},
    "CHA": {"division": "Southeast", "conference": "East"},
    "CHI": {"division": "Central", "conference": "East"},
    "CLE": {"division": "Central", "conference": "East"},
    "DET": {"division": "Central", "conference": "East"},
    "IND": {"division": "Central", "conference": "East"},
    "MIA": {"division": "Southeast", "conference": "East"},
    "MIL": {"division": "Central", "conference": "East"},
    "NYK": {"division": "Atlantic", "conference": "East"},
    "ORL": {"division": "Southeast", "conference": "East"},
    "PHI": {"division": "Atlantic", "conference": "East"},
    "TOR": {"division": "Atlantic", "conference": "East"},
    "WAS": {"division": "Southeast", "conference": "East"},
    
    # Western Conference
    "DAL": {"division": "Southwest", "conference": "West"},
    "DEN": {"division": "Northwest", "conference": "West"},
    "GSW": {"division": "Pacific", "conference": "West"},
    "HOU": {"division": "Southwest", "conference": "West"},
    "LAC": {"division": "Pacific", "conference": "West"},
    "LAL": {"division": "Pacific", "conference": "West"},
    "MEM": {"division": "Southwest", "conference": "West"},
    "MIN": {"division": "Northwest", "conference": "West"},
    "NOP": {"division": "Southwest", "conference": "West"},
    "OKC": {"division": "Northwest", "conference": "West"},
    "PHX": {"division": "Pacific", "conference": "West"},
    "POR": {"division": "Northwest", "conference": "West"},
    "SAC": {"division": "Pacific", "conference": "West"},
    "SAS": {"division": "Southwest", "conference": "West"},
    "UTA": {"division": "Northwest", "conference": "West"},

    # Defunct teams
    "SEA": {"division": "Northwest", "conference": "West"},  # Seattle SuperSonics
    "VAN": {"division": "Southwest", "conference": "West"},  # Vancouver Grizzlies
    "NJN": {"division": "Atlantic", "conference": "East"},   # New Jersey Nets
    "NOH": {"division": "Southwest", "conference": "West"},  # New Orleans Hornets
    "NOK": {"division": "Southwest", "conference": "West"},  # New Orleans/Oklahoma City Hornets
    "KCK": {"division": "Pacific", "conference": "West"},    # Kansas City Kings
    "GOS": {"division": "Pacific", "conference": "West"},    # Golden State Warriors
    "SDC": {"division": "Pacific", "conference": "West"},    # San Diego Clippers
    "UTH": {"division": "Northwest", "conference": "West"},  # Utah Jazz
    "CHH": {"division": "Southeast", "conference": "East"},  # Charlotte Hornets
    "PHL": {"division": "Atlantic", "conference": "East"},   # Philadelphia 76ers
    "SAN": {"division": "Southwest", "conference": "West"},  # San Antonio Spurs
}

def remove_player_profile_fields(player_info):
    """
    Remove specified fields from player profile.
    """
    if 'profile' in player_info:
        # Fields to remove
        fields_to_remove = [
            'PERSON_ID', 
            'DISPLAY_LAST_COMMA_FIRST', 
            'DISPLAY_FI_LAST', 
            'PLAYER_SLUG', 
            'LAST_AFFILIATION',
            'JERSEY',
            'TEAM_CODE',
            'TEAM_CITY',
            'PLAYERCODE',
        ]
        
        # Remove each field if it exists
        for field in fields_to_remove:
            if field in player_info['profile']:
                del player_info['profile'][field]
    
    return player_info

def add_team_division_conference(team_info, team_abbr):
    """
    Add division and conference information to team profile.
    """
    if team_abbr in team_divisions:
        if 'profile' not in team_info:
            team_info['profile'] = {}
        
        team_info['profile']['DIVISION'] = team_divisions[team_abbr]['division']
        team_info['profile']['CONFERENCE'] = team_divisions[team_abbr]['conference']
    
    return team_info

def process_game(game, skip_sdc_after_1986=False):
    """
    Process a single game to:
    1. Replace defunct team abbreviations with active ones
    2. Add game location and opponent information
    3. Process season ID to determine season type and year
    4. Add opponent division and conference information
    5. Add flags for conference and division games
    
    Args:
        game: The game data dictionary
        skip_sdc_after_1986: Whether to check for and skip SDC games after 1986
    
    Returns:
        True if the game should be included, False if it should be filtered out
    """
    # Check for SDC games after 1986 if requested
    if skip_sdc_after_1986 and game.get('TEAM_ABBREVIATION') == "SDC" and 'GAME_DATE' in game:
        try:
            game_year = int(game['GAME_DATE'].split('-')[0])
            if game_year >= 1986:
                return False
        except (ValueError, IndexError):
            pass
    
    # Replace defunct team abbreviation with active one
    team_abbr = game.get('TEAM_ABBREVIATION')
    if team_abbr in defunct_team_abbr_to_id:
        team_id = defunct_team_abbr_to_id[team_abbr]
        if team_id in id_to_team_abbr:
            game['TEAM_ABBREVIATION'] = id_to_team_abbr[team_id]
    
    # Process matchup for game location and opponent
    if 'MATCHUP' in game:
        matchup = game['MATCHUP']
        
        # Extract team and opponent from matchup
        if ' vs. ' in matchup:
            game['GAME_LOCATION'] = 'home'
            team_abbr, opponent_abbr = matchup.split(' vs. ')
        elif ' @ ' in matchup:
            game['GAME_LOCATION'] = 'road'
            team_abbr, opponent_abbr = matchup.split(' @ ')
        else:
            game['GAME_LOCATION'] = 'unknown'
            team_abbr, opponent_abbr = 'unknown', 'unknown'
        
        # Replace defunct team abbreviations in both parts of the matchup
        if team_abbr in defunct_team_abbr_to_id:
            team_id = defunct_team_abbr_to_id[team_abbr]
            if team_id in id_to_team_abbr:
                team_abbr = id_to_team_abbr[team_id]
        
        if opponent_abbr in defunct_team_abbr_to_id:
            team_id = defunct_team_abbr_to_id[opponent_abbr]
            if team_id in id_to_team_abbr:
                opponent_abbr = id_to_team_abbr[team_id]
        
        # Reconstruct matchup with active team abbreviations
        if game['GAME_LOCATION'] == 'home':
            game['MATCHUP'] = f"{team_abbr} vs. {opponent_abbr}"
        elif game['GAME_LOCATION'] == 'road':
            game['MATCHUP'] = f"{team_abbr} @ {opponent_abbr}"
        
        # Add opponent field
        game['OPPONENT'] = opponent_abbr
        
        # Add opponent full name if available
        if opponent_abbr in team_abbr_to_team_name:
            game['OPPONENT_NAME'] = team_abbr_to_team_name[opponent_abbr]
            
        # Add opponent division and conference information
        if opponent_abbr in team_divisions:
            game['OPPONENT_DIVISION'] = team_divisions[opponent_abbr]['division']
            game['OPPONENT_CONFERENCE'] = team_divisions[opponent_abbr]['conference']
            
            # Add flags for conference and division games
            if team_abbr in team_divisions:
                game['CONFERENCE_GAME'] = (team_divisions[team_abbr]['conference'] == team_divisions[opponent_abbr]['conference'])
                game['DIVISION_GAME'] = (team_divisions[team_abbr]['division'] == team_divisions[opponent_abbr]['division'])
    
    # Process SEASON_ID to determine season type and year
    if 'SEASON_ID' in game:
        season_id = game['SEASON_ID']
        
        # First digit indicates season type
        if season_id.startswith('2'):
            game['SEASON_TYPE'] = 'Regular Season'
        elif season_id.startswith('4'):
            game['SEASON_TYPE'] = 'Playoffs'
        elif season_id.startswith('5'):
            game['SEASON_TYPE'] = 'Play-In Tournament'
        elif season_id.startswith('6'):
            game['SEASON_TYPE'] = 'NBA Cup Finals'
        else:
            game['SEASON_TYPE'] = 'Unknown'
        
        # Extract year from season ID (remaining digits)
        try:
            year = int(season_id[1:])
            game['SEASON_YEAR'] = f"{year}-{(year % 100) + 1}"
        except ValueError:
            game['SEASON_YEAR'] = 'Unknown'
    
    return True

def process_nba_data(input_file, output_file):
    """
    Process NBA team data:
    1. Replace defunct team abbreviations with active ones
    2. Add game location, opponent, season type, and season year to each game
    3. Add division and conference information to team profiles
    4. Add opponent division/conference information to games
    5. Add flags for conference and division games
    """
    # Load the JSON data
    with open(input_file, 'r') as f:
        teams_data = json.load(f)
    
    # Process each team
    for team_name, team_info in teams_data.items():
        # Skip if no games data
        if 'games' not in team_info:
            continue

        # Add division and conference to team profile
        if 'profile' in team_info and team_info['profile']['ABBREVIATION'] in team_divisions:
            team_info = add_team_division_conference(team_info, team_info['profile']['ABBREVIATION'])
        elif team_name in team_abbr_to_team_name.values():
            # Try to find the abbreviation from the team name
            for abbr, name in team_abbr_to_team_name.items():
                if name == team_name:
                    team_info = add_team_division_conference(team_info, abbr)
                    break
        
        # Process each game
        if isinstance(team_info['games'], dict):
            for date, game in team_info['games'].items():
                process_game(game)
        elif isinstance(team_info['games'], list):
            for game in team_info['games']:
                process_game(game)
    
    # Save the processed data
    with open(output_file, 'w') as f:
        json.dump(teams_data, f, indent=2)
    
    print(f"Processed data saved to {output_file}")

def filter_players_data(input_file, output_file):
    """
    Filter and process the players data JSON:
    1. Exclude players with no games
    2. Exclude players with GAMES_PLAYED_FLAG set to "N"
    3. Exclude games from non-NBA teams (G-League, All-Star games, etc.)
    4. Exclude games with "SDC" team abbreviation from 1986 onwards
    5. Replace defunct team abbreviations with active ones
    6. Add game location, opponent, season type, and season year to each game
    7. Add opponent division/conference information to games
    8. Add flags for conference and division games
    9. Remove specified fields from player profiles
    10. Only save filtered and processed data to the output file
    """
    # Load the player data
    with open(input_file, 'r') as f:
        players_data = json.load(f)
    
    # Valid team abbreviations (combine current and defunct)
    valid_team_abbrs = set(list(team_abbr_to_id.keys()) + list(defunct_team_abbr_to_id.keys()))
    
    # Track statistics
    players_removed = 0
    games_removed = 0
    total_games_before = 0
    total_games_after = 0
    
    # Create a new dictionary for filtered data
    filtered_players_data = {}
    
    # Process each player
    for player_id, player_info in players_data.items():
        # Skip players without games
        if 'games' not in player_info or not player_info['games']:
            players_removed += 1
            continue
            
        # Skip players with GAMES_PLAYED_FLAG set to "N"
        if 'profile' in player_info and player_info['profile'].get('GAMES_PLAYED_FLAG') == "N":
            players_removed += 1
            continue
        
        # Remove specified fields from player profile
        player_info = remove_player_profile_fields(player_info)
        
        if isinstance(player_info['games'], list):
            # Handle list format
            total_games_before += len(player_info['games'])
            
            # Filter out non-NBA games and process the rest
            filtered_games = []
            for game in player_info['games']:
                # Check if the game is from a valid NBA team
                team_abbr = game.get('TEAM_ABBREVIATION')
                
                # Skip invalid teams
                if team_abbr not in valid_team_abbrs:
                    games_removed += 1
                    continue
                
                # Process game data - returns False if game should be skipped
                if not process_game(game, skip_sdc_after_1986=True):
                    games_removed += 1
                    continue
                
                # Include the game if it passed all filters
                filtered_games.append(game)
            
            # Only include player if they have valid NBA games
            if filtered_games:
                # Create a copy of player_info with filtered games
                filtered_player = player_info.copy()
                filtered_player['games'] = filtered_games
                filtered_players_data[player_id] = filtered_player
                total_games_after += len(filtered_games)
            else:
                players_removed += 1
                
        elif isinstance(player_info['games'], dict):
            # Handle dictionary format
            total_games_before += len(player_info['games'])
            
            # Filter out non-NBA games and process the rest
            filtered_games = {}
            for date, game in player_info['games'].items():
                # Check if the game is from a valid NBA team
                team_abbr = game.get('TEAM_ABBREVIATION')
                
                # Skip invalid teams
                if team_abbr not in valid_team_abbrs:
                    games_removed += 1
                    continue
                
                # Check for SDC games from 1986 onwards
                if team_abbr == "SDC":
                    try:
                        # For dictionary format, the date might be in the key
                        if date.startswith('19'):  # Handle dates starting with year
                            game_year = int(date.split('-')[0])
                            if game_year >= 1986:
                                games_removed += 1
                                continue
                    except (ValueError, IndexError, AttributeError):
                        pass
                
                # Process game data
                process_game(game)
                
                # Include the game if it passed all filters
                filtered_games[date] = game
            
            # Only include player if they have valid NBA games
            if filtered_games:
                # Create a copy of player_info with filtered games
                filtered_player = player_info.copy()
                filtered_player['games'] = filtered_games
                filtered_players_data[player_id] = filtered_player
                total_games_after += len(filtered_games)
            else:
                players_removed += 1
    
    # Save the filtered data to output file
    with open(output_file, 'w') as f:
        json.dump(filtered_players_data, f, indent=2)
    
    # Print statistics
    print(f"Filtered player data saved to {output_file}")
    print(f"Players removed: {players_removed}")
    print(f"Players included: {len(filtered_players_data)}")
    print(f"Games removed: {games_removed}")
    print(f"Total games before filtering: {total_games_before}")
    print(f"Total games after filtering: {total_games_after}")

# Example usage
if __name__ == "__main__":
    # Team data processing
    team_input_file = "teams_data.json"
    team_output_file = "nba_teams_processed.json"
    process_nba_data(team_input_file, team_output_file)
    
    # Player data filtering
    player_input_file = "players_data.json"
    player_output_file = "nba_players_filtered.json"
    filter_players_data(player_input_file, player_output_file)