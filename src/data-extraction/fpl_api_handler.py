import requests
import pandas as pd

def get_json_data(url):
    """
    Get data from the FPL API.
    """
    response = requests.get(url)
    return response.json()

def get_static_data(key):
    """
    Get requested data key from bootstrap-static endpoint in dataframe format.

    Useful keys:
    - teams
    - events (GW overview for FPL)
    - elements (players)
    - element_types (player types)
    - elements_stats (map of player stats labels and column names)
    """
    URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
    data = get_json_data(URL)
    
    return pd.json_normalize(data[key])

def get_fixtures():
    """
    Get all upcoming fixtures from the fixtures endpoint in dataframe format.
    """
    URL = "https://fantasy.premierleague.com/api/fixtures/"
    data = get_json_data(URL)

    data = [fixture for fixture in data if fixture['event'] != None]

    for fixture in data:
        keys = fixture.keys()
        keys_to_remove = set(keys) - set(["team_h", "team_a", "event", "id", "team_h_difficulty", "team_a_difficulty"])
        for key in keys_to_remove:
            fixture.pop(key)

    return pd.json_normalize(data)

def get_player_info(element_id, key):
    """
    Get player history from the element_history endpoint in dataframe format.

    Possible keys:
    - history
    - fixtures
    """
    URL = f"https://fantasy.premierleague.com/api/element-summary/{element_id}/"
    data = get_json_data(URL)

    data = data[key]

    return pd.json_normalize(data)

def get_manager_squad(manager_id, gw):
    """
    Get manager squad for a given gameweek
    """
    URL = f"https://fantasy.premierleague.com/api/entry/{manager_id}/event/{gw}/picks/"
    data = get_json_data(URL)
    data = data["picks"]
    return pd.json_normalize(data)

def get_manager_info(manager_id):
    """
    Get info for a praticular manager from the element_summary endpoint in dataframe format.
    """
    URL = f"https://fantasy.premierleague.com/api/entry/{manager_id}/"
    data = get_json_data(URL)
    data.pop("leagues")
    
    return data