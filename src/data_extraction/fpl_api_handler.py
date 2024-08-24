import requests
from enum import Enum
from pydantic_models import *

class FPLAPIEndpoint(Enum):
    BOOTSTRAP_STATIC = "bootstrap-static/"
    FIXTURES = "fixtures/"
    ELEMENT_SUMMARY = "element-summary/"
    ENTRY = "entry/"
    PICKS = "entry/{manager_id}/event/{gw}/picks/"

class FPLAPIHandler:
    def __init__(self, base_url="https://fantasy.premierleague.com/api/"):
        self.base_url = base_url

    def _make_request(self, method, endpoint, **kwargs):
        url = self.base_url + endpoint
        response = requests.request(method, url, **kwargs)
        return response.json()

    def get_json_data(self, endpoint, **kwargs):
        return self._make_request("GET", endpoint, **kwargs)

    def post_json_data(self, endpoint, data, **kwargs):
        return self._make_request("POST", endpoint, json=data, **kwargs)

    def get_return_type_for_static_data(self, key):
        if key == "events":
            return Event
        elif key == "teams":
            return Team
        elif key == "elements":
            return Element
        elif key == "element_types":
            return ElementType
        elif key == "element_stats":
            return ElementStat
        else:
            raise ValueError(f"Invalid key: {key}")
    
    def get_static_data(self, key, **kwargs):
        data = self.get_json_data(FPLAPIEndpoint.BOOTSTRAP_STATIC.value, **kwargs)
        return_type = self.get_return_type_for_static_data(key)
        return [return_type.model_validate(item) for item in data[key]]

    def get_fixtures(self, **kwargs):
        data = self.get_json_data(FPLAPIEndpoint.FIXTURES.value, **kwargs)
        return [Fixture.model_validate(fixture) for fixture in data]

    def get_player_info(self, element_id, key, **kwargs):
        endpoint = FPLAPIEndpoint.ELEMENT_SUMMARY.value + f"{element_id}/"
        data = self.get_json_data(endpoint, **kwargs)[key]
        if key == "history":
            return [PlayerHistory.model_validate(item) for item in data]
        elif key == "fixtures":
            return [PlayerFixture.model_validate(item) for item in data]

    def get_manager_squad(self, manager_id, gw, **kwargs):
        endpoint = FPLAPIEndpoint.PICKS.value.format(manager_id=manager_id, gw=gw)
        data = self.get_json_data(endpoint, **kwargs)["picks"]
        return [ManagerPick.model_validate(item) for item in data]

    def get_manager_info(self, manager_id, **kwargs):
        endpoint = FPLAPIEndpoint.ENTRY.value + f"{manager_id}/"
        data = self.get_json_data(endpoint, **kwargs)
        return ManagerInfo.model_validate(data)

if __name__ == "__main__":
    fpl_handler = FPLAPIHandler()
    # print("Getting static data...")
    # print("\tGetting events...")
    # static_data = fpl_handler.get_static_data("events")
    # print("Static data:", static_data)

    # print("\tGetting teams...")
    # static_data = fpl_handler.get_static_data("teams")
    # print("Static data:", static_data)

    print("\tGetting players...")
    static_data = fpl_handler.get_static_data("elements")
    print("Static data:", static_data)

    # print("\tGetting player types...")
    # static_data = fpl_handler.get_static_data("element_types")
    # print("Static data:", static_data)

    # print("\tGetting element stats...")
    # static_data = fpl_handler.get_static_data("element_stats")
    # print("Static data:", static_data)

    # print("Getting fixtures...")
    # fixtures = fpl_handler.get_fixtures()
    # print("Fixtures:", fixtures)

    # print("Getting player history info...")
    # player_info = fpl_handler.get_player_info(1, "history")
    # print("Player info:", player_info)

    # print("Getting player fixture info...")
    # player_fixture_info = fpl_handler.get_player_info(1, "fixtures")
    # print("Player fixture info:", player_fixture_info)

    # print("Getting manager squad...")
    # manager_squad = fpl_handler.get_manager_squad(1, 1)
    # print("Manager squad:", manager_squad)

    # print("Getting manager info...")
    # manager_info = fpl_handler.get_manager_info(1)
    # print("Manager info:", manager_info)