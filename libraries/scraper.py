import requests

API_LINK = "https://content.osu.edu/v2/library/locations"


def get_response():
    return requests.get(API_LINK).json()


class Scraper:
    def __init__(self, main_campus=True):
        self.is_on_main_campus = main_campus

    def get_libraries(self):
        library_list = []

        response = get_response()
        for library in response["data"]["locations"]:
            if library["isOnMainCampus"] == self.is_on_main_campus:
                library_list.append(library)

        return library_list
