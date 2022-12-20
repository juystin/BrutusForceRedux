import requests
import re
from bs4 import BeautifulSoup

BUILDING_API_LINK = "https://content.osu.edu/v2/buildings/"
CLASSROOM_LINK = "https://odee.osu.edu/classroom-search/"


def get_building_response():
    return requests.get(BUILDING_API_LINK).json()


def get_classroom_response():
    return BeautifulSoup(requests.get(CLASSROOM_LINK).content, features="html.parser")


def parse_building_div(div_element):
    building_name = div_element.h3.a.string
    classrooms = []

    classroom_divs = div_element.find_all('div', {'class': 'views-field views-field-title'})
    for classroom_element in classroom_divs:
        classrooms.append(re.search("\d+", classroom_element.span.a.string)[0])

    return {'building_name': building_name, 'classrooms': classrooms}


class Scraper:
    # Optional building number list parameter.
    # If not supplied, then grab information of every building on campus.
    def __init__(self, building_number_list=None):
        self.building_numbers = building_number_list

    def get_buildings(self):
        building_list = []

        building_response = get_building_response()
        classroom_response = get_classroom_response()
        for building in building_response["data"]["buildings"]:
            if (self.building_numbers is None) or (building["buildingNumber"] in self.building_numbers):
                building_list.append(building)

        for div_element in classroom_response.find_all('div', {'class': 'views-accordion-grouped-row'}):
            building_classroom_list = parse_building_div(div_element)
            for building in building_list:
                if building['name'].split()[0] == building_classroom_list['building_name'].split()[0]:
                    building['classrooms'] = building_classroom_list['classrooms']

        return building_list
