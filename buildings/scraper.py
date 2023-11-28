import requests
import re

from tqdm import tqdm

BUILDING_API_LINK = "https://content.osu.edu/v2/api/buildings"

def get_building_response():
    return requests.get(BUILDING_API_LINK).json()


class Scraper:
    # Optional building number list parameter.
    # If not supplied, then grab information of every building on campus.
    def __init__(self, building_number_list=None):
        self.building_numbers = building_number_list

    def get_buildings(self):
        building_list = []

        building_response = get_building_response()
        for building in tqdm(building_response["data"]["buildings"], desc="Parsing buildings..."):
            if (self.building_numbers is None) or (building["buildingNumber"] in self.building_numbers):
                building_list.append(building)

        return building_list

