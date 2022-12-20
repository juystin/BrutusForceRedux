import time
from datetime import datetime

import requests
import itertools

BASE_API_LINK = "https://content.osu.edu/v2/classes/search?q="

# Sort by subject is required for the output to be correct.
# API is buggy when sorting by relevance (default) and sorting by catalog number.
BASE_PARAMS = {
    "p": "1",
    "term": "1232",
    "campus": "col",
    "sort": "subject"
}

def convert_to_24_hr(time):
    if time is None:
        return time

    if time[1] == ":":
        time = "0" + time

    if time[6:] == "pm" and time[0:2] != "12":
        time = str((int(time[0:2])) + 12) + time[2:]

    return time[0:5]


def get_duration(start_time, end_time):
    if start_time is None or end_time is None:
        return "0:00"
    return str(datetime.strptime(end_time, "%H:%M") - datetime.strptime(start_time, "%H:%M"))[:-3]


def get_response_with_params(params):
    link_with_params = BASE_API_LINK
    for param, value in params.items():
        link_with_params = link_with_params + "&" + str(param) + "=" + str(value)
    return requests.get(link_with_params).json()


def get_filter_data(filters):
    response = get_response_with_params(BASE_PARAMS)

    filter_data = []

    for filter_name in filters:
        filter_options = []
        for filter_type in response["data"]["filters"]:
            if filter_type["slug"] == filter_name:
                for option in filter_type["items"]:
                    filter_options.append(option["term"])
        filter_data.append({
            filter_name: filter_options
        })

    return filter_data


def parse_response(params):
    response = get_response_with_params(params)

    class_meetings = []

    total_pages = response["data"]["totalPages"]

    for current_page in range(1, total_pages + 1):
        params["p"] = str(current_page)
        response = get_response_with_params(params)

        for course in response["data"]["courses"]:
            try:
                class_title = course["course"]["title"]
            except KeyError as e:
                print("NO TITLE ERROR")
                print(course)
                print(e)
                class_title = course["course"]["description"].splitlines()[0]
            class_description = course["course"]["description"].splitlines()[0]
            class_subject = course["course"]["subject"]
            class_number = course["course"]["catalogNumber"]
            try:
                units = course["course"]["maxUnits"]
            except KeyError as e:
                print("NO UNITS ERROR")
                print(course)
                print(e)
                units = 0

            for section in course["sections"]:
                class_type = section["component"]

                for meeting in section["meetings"]:
                    facility_id = meeting["facilityId"]
                    building_name = meeting["facilityDescription"]
                    building_number = meeting["buildingCode"]
                    start_time = convert_to_24_hr(meeting["startTime"])
                    end_time = convert_to_24_hr(meeting["endTime"])

                    for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                        if meeting[day]:
                            class_meetings.append({
                                "Class Title": class_title,
                                "Class Description": class_description,
                                "Class Subject": class_subject,
                                "Class Number": class_number,
                                "Class Type": class_type,
                                "Units": units,
                                "Facility ID": facility_id,
                                "Building Name": building_name,
                                "Building Number": building_number,
                                "Day": day,
                                "Start Time": start_time,
                                "End Time": end_time,
                                "Duration": get_duration(start_time, end_time)
                            })

    return class_meetings

def get_classes_by_filter(raw_data):
    class_meetings = []
    parsed_data = []

    for i in range(0, len(raw_data)):
        filter_list = []
        filter_option = list(raw_data[i])[0]

        for filter_type in raw_data[i][filter_option]:
            filter_list.append({filter_option: filter_type})

        parsed_data.append(filter_list)

    filter_combinations = list(itertools.product(*parsed_data))

    for filter_combo in filter_combinations:
        params = BASE_PARAMS
        for filter_info in filter_combo:
            params[list(filter_info)[0]] = filter_info[list(filter_info)[0]]
        class_meetings.extend(parse_response(params))

    return class_meetings


class Scraper:
    def __init__(self, filters=['academic-career', 'component']):
        self.filters = filters

    def get_classes(self):
        filter_data = get_filter_data(self.filters)

        class_list = get_classes_by_filter(filter_data)

        return class_list
