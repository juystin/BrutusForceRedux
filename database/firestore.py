import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from tqdm import tqdm

# Taken from the Wiki (https://cloud.google.com/firestore/docs/manage-data/delete-data#python_2)
def delete_collection(coll_ref, batch_size):
    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

class Firestore:

    def __init__(self, location):
        self.location = location
        
        key = credentials.Certificate(self.location)
        app = firebase_admin.initialize_app(key)
        self.db = firestore.client()

    def init_classes(self, table_name):        
        delete_collection(self.db.collection(table_name), 100)
        self.classes_table = self.db.collection(table_name)

    def init_instructors(self, table_name):
        delete_collection(self.db.collection(table_name), 100)
        self.instructors_table = self.db.collection(table_name)

    def init_faculty(self, table_name):
        delete_collection(self.db.collection(table_name), 100)
        self.faculty_table = self.db.collection(table_name)

    def init_buildings(self, table_name):
        delete_collection(self.db.collection(table_name), 100)
        self.buildings_table = self.db.collection(table_name)

    def init_classrooms(self, table_name):
        delete_collection(self.db.collection(table_name), 100)
        self.classrooms_table = self.db.collection(table_name)

    def init_libraries(self, table_name):
        delete_collection(self.db.collection(table_name), 100)
        self.libraries_table = self.db.collection(table_name)

    def insert_class_list(self, class_list):
        faculty = []
        classrooms = []

        if len(class_list) > 0:
            for meeting in tqdm(class_list, desc="Inserting classes...", position=0):
                self.classes_table.add({
                    "building_num": meeting["Building Number"],
                    "class_title": meeting["Class Title"],
                    "class_desc": meeting["Class Description"],
                    "units": meeting["Units"],
                    "class_type": meeting["Class Type"],
                    "class_subject": meeting["Class Subject"],
                    "class_code": meeting["Class Code"],
                    "facility_id": meeting["Facility ID"],
                    "sunday": "sunday" in meeting["Days"],
                    "monday": "monday" in meeting["Days"],
                    "tuesday": "tuesday" in meeting["Days"],
                    "wednesday": "wednesday" in meeting["Days"],
                    "thursday": "thursday" in meeting["Days"],
                    "friday": "friday" in meeting["Days"],
                    "saturday": "saturday" in meeting["Days"],
                    "start_time": meeting["Start Time"],
                    "end_time": meeting["End Time"],
                    "class_duration": meeting["Duration"],
                    "class_number": meeting["Class Number"],
                    "section_number": meeting["Section Number"]
                })
                for instructor in tqdm(meeting["Instructors"], desc="Inserting instructors...", position=1, leave=False):
                    self.instructors_table.add({
                        "class_number": meeting["Class Number"],
                        "section_number": meeting["Section Number"],
                        "instructor_id": instructor["email"].split('@')[0] if instructor["email"] else None
                    }) 
                    
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
                        self.classrooms_table.add({
                            "building_num": building["Building Number"],
                            "facility_id": facility["Facility ID"],
                            "building_name": building["Building Name"],
                            "classroom_number": facility["Classroom Number"]
                        })

            for person in tqdm(faculty, desc="Inserting faculty..."):
                self.faculty_table.add({
                    "name": person["Name"],
                    "email": person["Email"],
                    "id": person["ID"]
                })

    def insert_building_list(self, building_list):
        if len(building_list) > 0:
            for building in tqdm(building_list, desc="Inserting buildings..."):
                self.buildings_table.add({
                    "building_num": building["buildingNumber"],
                    "building_name": building["name"],
                    "building_abbriev": building["buildingCode"],
                    "address": building["address"],
                    "lat": building["latitude"],
                    "lng": building["longitude"]
                })

    def insert_library_list(self, library_list):
        if len(library_list) > 0:
            for library in tqdm(library_list, desc="Inserting libraries..."):
                self.libraries_table.add({
                    "building_num": library["buildingNumber"],
                    "library_name": library["title"],
                    "library_abbriev": library["code"],
                    "address": library["address"],
                    "lat": library["latitude"],
                    "lng": library["longitude"],
                    "hours": library["hours"]
                })