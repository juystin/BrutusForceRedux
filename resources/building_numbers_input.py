import os

INPUT_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'building_numbers.txt'))

def load_from_file():
    with open(INPUT_FILE_PATH) as f:
        lines = [line.rstrip() for line in f]
    return lines