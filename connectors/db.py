import os
import sqlite3
import mysql.connector
from mysql.connector import Error

# Turn these into config
INPUT_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'building_numbers.txt'))
DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'brutusforce.db'))
DRIVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'chromedriver'))


def load_building_numbers():
    with open(INPUT_FILE_PATH) as f:
        lines = [line.rstrip() for line in f]
    return lines


def create_local_connection():
    return sqlite3.connect(DATABASE_NAME)

def create_remote_connection(user, password, host, port, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            port=port,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection