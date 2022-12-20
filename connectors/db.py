import os
import sqlite3

# Turn these into config
INPUT_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'building_numbers.txt'))
DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'brutusforce.db'))
DRIVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'chromedriver'))


def load_building_numbers():
    with open(INPUT_FILE_PATH) as f:
        lines = [line.rstrip() for line in f]
    return lines


def create_connection():
    return sqlite3.connect(DATABASE_NAME)
