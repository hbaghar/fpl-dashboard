import requests
from enum import Enum
from fpl_dashboard.data.database_model import *
from tqdm import tqdm
import typing
from multiprocessing import Pool
from sqlmodel import Session, create_engine, select

__all__ = (
    "FPLAPIHandler",
    "FPLAPIEndpoint",
    "populate_db",
)

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
        try:
            return response.json()
        except:
            raise ValueError(f"Invalid response from FPL API: {url}, {response.text}")

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
    
    def get_player_data(self, element):
        try:
            player_history = self.get_player_info(element.id, "history")
        except:
            print(f"Failed to get player data for element id {element.id}")
        return player_history


def populate_db():
    import os
    engine = create_engine("sqlite:///fpl_dashboard.db", echo=True)
    api = FPLAPIHandler()

    if os.path.exists("fpl_dashboard.db"):
        os.remove("fpl_dashboard.db")
    
    create_db_and_tables()

    events = api.get_static_data("events")
    elements = api.get_static_data("elements")
    teams = api.get_static_data("teams")
    element_types = api.get_static_data("element_types")
    fixtures = api.get_fixtures()
    
    player_history = []
    
    with Pool(16) as p:
        with tqdm(total=len(elements), desc="Retrieving player gameweek data") as pbar:
            for _, data in enumerate(
                p.imap(api.get_player_data, elements)
            ):
                player_history.extend(data)
                pbar.update()

    with Session(engine) as session:
        session.add_all(events)
        session.add_all(elements)
        session.add_all(teams)
        session.add_all(element_types)
        session.add_all(fixtures)
        session.add_all(player_history)

        session.commit()

if __name__ == "__main__":
    populate_db()

    engine = create_engine("sqlite:///fpl_dashboard.db", echo=True)
    with Session(engine) as session:
        mosalah = session.exec(select(Element).where(Element.second_name == "Salah")).one()
        print(mosalah.player_team.short_name, mosalah.player_position.singular_name_short,
              mosalah.away_stats, mosalah.away_stats_per_90)
