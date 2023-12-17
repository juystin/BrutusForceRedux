import classes
import buildings
import libraries
import resources
import database
import re
import time
import os
from enum import Enum


print("\n    ########    ########    ##      ##  ##########  ##      ##   ########")
print("    ##     ##   ##     ##   ##      ##      ##      ##      ##  ##      ##")
print("    ##      ##  ##      ##  ##      ##      ##      ##      ##  ##")
print("    ##      ##  ##      ##  ##      ##      ##      ##      ##  ##")
print("    #########   #########   ##      ##      ##      ##      ##    ######")
print("    ##      ##  ##      ##  ##      ##      ##      ##      ##          ##")
print("    ##      ##  ##      ##  ##      ##      ##      ##      ##          ##")
print("    ##      ##  ##      ##  ##      ##      ##      ##      ##  ##      ##")
print("    #########   ##      ##    ######        ##        ######     ########")
print("                                                                       ")
print("     #### ####     ##########  ##########  ########    ##########  #########")
print("   ####### ####    ##          ##      ##  ##     ##   ##          ## ")
print("  ####### ######   ##          ##      ##  ##      ##  ##          ## ")
print("  #######  #####   ##          ##      ##  ##      ##  ##          ## ")
print("  ######    #####  #######     ##      ##  #########   ##          #######")
print("  #######   #####  ##          ##      ##  ##      ##  ##          ##")
print("  ######## ######  ##          ##      ##  ##      ##  ##          ##")
print("    ####### #####  ##          ##      ##  ##      ##  ##          ##")
print("      #### ####    ##          ##########  ##      ##  ##########  #########\n")

class_scraper = classes.Scraper(resources.building_numbers_input.load_from_file())
building_scraper = buildings.Scraper(resources.building_numbers_input.load_from_file())
library_scraper = libraries.Scraper()

user_input = None
Storage = Enum('Storage', ['LOCAL', 'SQL', 'FIRESTORE'])

class_list = []
building_list = []
library_list = []

classes_table_name = "classes"
classrooms_table_name = "classrooms"
instructors_table_name = "instructors"
faculty_table_name = "faculty"
buildings_table_name = "buildings"
libraries_table_name = "libraries"

while (user_input != "local") and (user_input != "remote") and (user_input != "l") and (user_input != "r"):
    print("Database storage option (local/remote/l/r): ")
    user_input = input()

if (user_input == "local") or (user_input == "l"):
    user_storage = Storage.LOCAL
    # print("Enter location to save new database (leave empty for default): ")
    # user_location = input()
    # if user_location == "":
    #     user_location = None
    local_database = database.local.LocalSql()

elif (user_input == "remote") or (user_input == "r"):
    while (user_input != "sql") and (user_input != "firestore"):
        print("Database storage type (sql/firestore): ")
        user_input = input()
        
    if (user_input == "sql"):
        user_storage = Storage.SQL
        print("Enter username: ")
        user = input()
        print("Enter password: ")
        password = input()
        print("Enter host: ")
        host = input()
        remote_database = database.remote.RemoteSql(host, user, password)
        
    elif (user_input == "firestore"):
        user_storage = Storage.FIRESTORE
  
        # ASK FOR USER KEY LOCATION

        key_file = os.path.join(os.path.dirname(__file__), 'data', 'keys', 'firebase.json')
        firestore = database.firestore.Firestore(key_file)

while (user_input != "exit") and (user_input != "quit") and (user_input != "q"):
    print("\nCommands:  all:               Runs all three scrapers.")
    print("           class/c:           Runs only class scraper.")
    print("           building/b:     Runs only building scraper.")
    print("           library/l:       Runs only library scraper.")
    print("------------------------------------------------------")
    user_input = input()

    redundancy = True

    if user_input == "all":
        print("Run a redundancy check? (Y/n): ")
        user_input = input()
        if (user_input == "n"):
            redundancy = False
        print("\nBeginning all scrapers...")
        class_list = class_scraper.get_classes()
        print("Finished scraping classes.")
        building_list = building_scraper.get_buildings()
        print("Finished scraping buildings.")
        library_list = library_scraper.get_libraries()
        print("Finished scraping libraries.")

        if user_storage == Storage.LOCAL:
            local_database.init_classes(classes_table_name)
            local_database.init_instructors(instructors_table_name)
            local_database.init_faculty(faculty_table_name)
            local_database.init_buildings(buildings_table_name)
            local_database.init_classrooms(classrooms_table_name)
            local_database.init_libraries(libraries_table_name)
        elif user_storage == Storage.SQL:
            remote_database.init_classes(classes_table_name)
            remote_database.init_instructors(instructors_table_name)
            remote_database.init_faculty(faculty_table_name)
            remote_database.init_buildings(buildings_table_name)
            remote_database.init_classrooms(classrooms_table_name)
            remote_database.init_libraries(libraries_table_name)
        elif user_storage == Storage.FIRESTORE:
            firestore.init_classes(classes_table_name)
            firestore.init_instructors(instructors_table_name)
            firestore.init_faculty(faculty_table_name)
            firestore.init_buildings(buildings_table_name)
            firestore.init_classrooms(classrooms_table_name)
            firestore.init_libraries(libraries_table_name)

        break
    elif (user_input == "class") or (user_input == "c"):
        print("\nBeginning class scraper...")
        class_list = class_scraper.get_classes()
        print("Finished scraping classes.")
        print("Run a redundancy check? (Y/n): ")
        user_input = input()
        if (user_input == "n"):
            redundancy = False
        if user_storage == Storage.LOCAL:
            local_database.init_classes(classes_table_name)
            local_database.init_instructors(instructors_table_name)
            local_database.init_faculty(faculty_table_name)
            local_database.init_classrooms(classrooms_table_name)
        elif user_storage == Storage.SQL:
            remote_database.init_classes(classes_table_name)
            remote_database.init_instructors(instructors_table_name)
            remote_database.init_faculty(faculty_table_name)
            remote_database.init_classrooms(classrooms_table_name)
        elif user_storage == Storage.FIRESTORE:
            firestore.init_classes(classes_table_name)
            firestore.init_instructors(instructors_table_name)
            firestore.init_faculty(faculty_table_name)
            firestore.init_classrooms(classrooms_table_name)
        break
    elif (user_input == "building") or (user_input == "b"):
        print("\nBeginning buildings scraper...")
        building_list = building_scraper.get_buildings()
        print("Finished scraping buildings.")
        
        if user_storage == Storage.LOCAL:
            local_database.init_buildings(buildings_table_name)
        elif user_storage == Storage.SQL:
            remote_database.init_buildings(buildings_table_name)
        elif user_storage == Storage.FIRESTORE:
            firestore.init_buildings(buildings_table_name)
        break
    elif (user_input == "library") or (user_input == "l"):
        print("\nBeginning library scraper...")
        library_list = library_scraper.get_libraries()
        print("Finished scraping libraries.")
        
        if user_storage == Storage.LOCAL:
            local_database.init_libraries(libraries_table_name)
        elif user_storage == Storage.SQL:
            remote_database.init_libraries(libraries_table_name)
        elif user_storage == Storage.FIRESTORE:
            firestore.init_libraries(libraries_table_name) 
        break
    elif (user_input == "exit") or (user_input == "quit") or (user_input == "q"):
        print("Goodbye!")
        break

if (user_input != "exit") and (user_input != "quit") and (user_input != "q"):
    print("\nBeginning populating database...")

    if user_storage == Storage.LOCAL:
        local_database.insert_class_list(class_list)
        local_database.insert_building_list(building_list)
        local_database.insert_library_list(library_list)
        if (redundancy):
            local_database.remove_class_redundancies()
        local_database.close()
    elif user_storage == Storage.SQL:
        remote_database.insert_class_list(class_list)
        remote_database.insert_building_list(building_list)
        remote_database.insert_library_list(library_list)
        remote_database.close()
    elif user_storage == Storage.FIRESTORE:
        firestore.insert_class_list(class_list)
        firestore.insert_building_list(building_list)
        firestore.insert_library_list(library_list)
    print("Finished populating database.\n")