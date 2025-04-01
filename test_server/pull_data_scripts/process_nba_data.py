import json

def process_nba_data(input_file, output_file):
    # Load the JSON data
    with open(input_file, 'r') as f:
        teams_data = json.load(f)
    
    # Process each team
    for team_name, team_info in teams_data.items():
        # Skip if no games data
        if 'games' not in team_info:
            continue
        
        # Process each game
        for game in team_info['games']:
            if 'MATCHUP' in game:
                matchup = game['MATCHUP']
                
                # Determine if home or road game
                if ' vs. ' in matchup:
                    game['GAME_LOCATION'] = 'home'
                    # Extract opponent (team after "vs. ")
                    opponent = matchup.split(' vs. ')[1]
                elif ' @ ' in matchup:
                    game['GAME_LOCATION'] = 'road'
                    # Extract opponent (team after "@")
                    opponent = matchup.split(' @ ')[1]
                else:
                    game['GAME_LOCATION'] = 'unknown'
                    opponent = 'unknown'
                
                # Add opponent field
                game['OPPONENT'] = opponent
            
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
                else:
                    game['SEASON_TYPE'] = 'Unknown'
                
                # Extract year from season ID (remaining digits)
                try:
                    year = int(season_id[1:])
                    game['SEASON_YEAR'] = f"{year}-{(year % 100) + 1}"
                except ValueError:
                    game['SEASON_YEAR'] = 'Unknown'
    
    # Save the processed data
    with open(output_file, 'w') as f:
        json.dump(teams_data, f, indent=2)
    
    print(f"Processed data saved to {output_file}")

# Example usage
if __name__ == "__main__":
    input_file = "teams_data.json"  # Replace with your input file path
    output_file = "nba_teams_processed.json"  # Replace with desired output file path
    process_nba_data(input_file, output_file)