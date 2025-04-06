from push_new_nba_data import insert_data_from_json
import json

if __name__ == "__main__":
    insert_data_from_json("nba_teams_processed.json", "teams")