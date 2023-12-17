import os
import sqlite3

from tqdm import tqdm

class LocalSql:

    def __init__(self, location=None):
        if location is None:
            self.location = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'brutusforce.db'))
        else:
            self.location = location
        
        try:
            os.remove(self.location)
        except OSError:
            open(self.location, 'a').close()
            
        self.conn = sqlite3.connect(self.location)
        self.cursor = self.conn.cursor()

    def init_classes(self, table_name):
        self.cursor.execute('''
        CREATE TABLE ''' + table_name + '''
        (building_num text, class_title text, class_desc text, units text, class_type text, class_subject text, 
        class_code text, facility_id text, monday text, tuesday text, wednesday text, thursday text, friday text, 
        start_time text, end_time text, class_duration text, class_number text, section_number text)
        ''')
        self.classes_table = table_name

    def init_instructors(self, table_name):
        self.cursor.execute('''
        CREATE TABLE ''' + table_name + '''
        (class_number text, section_number text, instructor_id text)
        ''')
        self.instructors_table = table_name

    def init_faculty(self, table_name):
        self.cursor.execute('''
        CREATE TABLE ''' + table_name + '''
        (name text, email text, id text)
        ''')
        self.faculty_table = table_name

    def init_buildings(self, table_name):
        self.cursor.execute('''
        CREATE TABLE ''' + table_name + '''
        (building_num text, building_name text, building_abbriev text, address text, lat text, lng text)
        ''')
        self.buildings_table = table_name

    def init_classrooms(self, table_name):
        self.cursor.execute('''
        CREATE TABLE ''' + table_name + '''
        (building_num text, facility_id text, building_name text, classroom_number text)
        ''')
        self.classrooms_table = table_name

    def init_libraries(self, table_name):
        self.cursor.execute('''
        CREATE TABLE ''' + table_name + '''
        (building_num text, library_name text, library_abbriev text, address text, lat text, lng text,
        hours text)
        ''')
        self.libraries_table = table_name

    def insert_class_list(self, class_list):
        faculty = []
        classrooms = []

        if len(class_list) > 0:
            for meeting in tqdm(class_list, desc="Inserting classes...", position=0):              
                self.cursor.execute('''
                INSERT INTO ''' + self.classes_table + '''
                (building_num, class_title, class_desc, units, class_type, class_subject, 
                class_code, facility_id, monday, tuesday, wednesday, thursday, friday, 
                start_time, end_time, class_duration, class_number, section_number) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', [meeting["Building Number"], meeting["Class Title"], meeting["Class Description"], meeting["Units"],
                    meeting["Class Type"], meeting["Class Subject"], meeting["Class Code"], meeting["Facility ID"],
                    "monday" in meeting["Days"], "tuesday" in meeting["Days"], "wednesday" in meeting["Days"], "thursday" in meeting["Days"], 
                    "friday" in meeting["Days"], meeting["Start Time"], meeting["End Time"], meeting["Duration"],
                    meeting["Class Number"], meeting["Section Number"]])
                for instructor in tqdm(meeting["Instructors"], desc="Inserting instructors...", position=1, leave=False):
                    self.cursor.execute('''
                    INSERT INTO ''' + self.instructors_table + '''
                    (class_number, section_number, instructor_id)
                    VALUES (?, ?, ?)
                    ''', [meeting["Class Number"], meeting["Section Number"],
                        instructor["email"].split('@')[0] if instructor["email"] else None])
                    if instructor["name"]:
                        if (instructor["email"] and all(person["Email"] != instructor["email"] for person in faculty)) or (all(person["Name"] != instructor["name"] for person in faculty)):
                            faculty.append({
                                "Name": instructor["name"],
                                "Email": instructor["email"],
                                "ID": instructor["email"].split('@')[0] if instructor["email"] else None
                            })
                if (not any(building["Building Number"] == meeting["Building Number"] for building in classrooms)):
                    classrooms.append({
                        "Building Number": meeting["Building Number"],
                        "Building Name": meeting["Building Name"],
                        "Classrooms": [{
                            "Facility ID": meeting["Facility ID"],
                            "Classroom Number": meeting["Classroom Number"]
                        }]
                    })
                else:
                    for index, building in enumerate(classrooms):
                        if (building["Building Number"] == meeting["Building Number"]):
                            if (not any(facility["Facility ID"] == meeting["Facility ID"] for facility in building["Classrooms"])):
                                building["Classrooms"].append({
                                    "Facility ID": meeting["Facility ID"],
                                    "Classroom Number": meeting["Classroom Number"]
                                })

            for building in tqdm(classrooms, desc="Inserting classrooms...", position=0):
                for facility in tqdm(building["Classrooms"], desc="Reading " + str(len(building["Classrooms"])) + " classrooms from " + str(building["Building Name"]) + "...", position=1, leave=False):
                    if (facility["Facility ID"] != "ONLINE" and facility["Facility ID"] != "OFFCAMPUS"):
                        self.cursor.execute('''
                        INSERT INTO ''' + self.classrooms_table + '''
                        (building_num, facility_id, building_name, classroom_number)
                        VALUES (?, ?, ?, ?)
                        ''', [building["Building Number"], facility["Facility ID"], building["Building Name"], facility["Classroom Number"]])

            for person in tqdm(faculty, desc="Inserting faculty..."):
                self.cursor.execute('''
                INSERT INTO ''' + self.faculty_table + '''
                (name, email, id)
                VALUES (?, ?, ?)
                ''', [person["Name"], person["Email"], person["ID"]])

        self.conn.commit()

    def insert_building_list(self, building_list):
        
        if len(building_list) > 0:
            for building in tqdm(building_list, desc="Inserting buildings..."):
                self.cursor.execute('''
                INSERT INTO ''' + self.buildings_table + ''' (building_num, building_name, building_abbriev, address, lat, lng)
                VALUES (?, ?, ?, ?, ?, ?)''', [building["buildingNumber"], building["name"], building["buildingCode"],
                                            building["address"], building["latitude"], building["longitude"]])
        self.conn.commit()

    def insert_library_list(self, library_list):
        
        if len(library_list) > 0:
            for library in tqdm(library_list, desc="Inserting libraries..."):
                self.cursor.execute('''
                    INSERT INTO ''' + self.libraries_table + ''' (building_num, library_name, library_abbriev, address, lat, lng, hours)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''', [library["buildingNumber"], library["title"], library["code"],
                                                    library["address"], library["latitude"], library["longitude"],
                                                    library["hours"]])
        self.conn.commit()

    def remove_class_redundancies(self):

        self.cursor.execute('''
            DELETE FROM classes
            WHERE rowid NOT IN (SELECT min(rowid)
            FROM classes
            GROUP BY class_number, section_number, monday, tuesday, wednesday, thursday, friday, facility_id)
        ''')

        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()