import classes
import buildings
import libraries
import connectors

print("BRUTUS-FORCE Redux")
print("-----------------------------------------------------")

class_scraper = classes.Scraper()
building_scraper = buildings.Scraper(connectors.db.load_building_numbers())
library_scraper = libraries.Scraper()

user_input = None
local = None

class_list = []
building_list = []
library_list = []

while (user_input != "exit") and (user_input != "quit") and (user_input != "q"):
    print("Choose your database type: ")
    print("l/local: Creates a local sqlite3 file.")
    print("r/remote: Writes to a remote database.")
    print("exit/quit/q: Quits the program.")
    print("-----------------------------------------------------")
    user_input = input()
    if (user_input == "local") or (user_input == "l"):
        conn = connectors.db.create_local_connection()
        cursor = conn.cursor()
        local = True
        break
    if (user_input == "remote") or (user_input == "r"):
        print("Enter username: ")
        user = input()
        print("Enter password: ")
        password = input()
        print("Enter host: ")
        host = input()
        print("Enter port: ")
        port = input()
        print("Enter database name: ")
        db_name = input()
        conn = connectors.db.create_remote_connection(user, password, host, port, db_name)
        if not conn:
            print("Could not connect")
        else:
            cursor = conn.cursor()
            local = False
            break
    elif (user_input == "exit") or (user_input == "quit") or (user_input == "q"):
        print("Goodbye!")
        break

while (user_input != "exit") and (user_input != "quit") and (user_input != "q"):
    print("Commands:  all: Runs all three scrapers.")
    print("           class/c: Runs only class scraper.")
    print("           building/b: Runs only building scraper.")
    print("           library/l: Runs only library scraper.")
    print("           exit/quit/q: Quits the program.")
    print("-----------------------------------------------------")
    user_input = input()

    if user_input == "all":
        print("Beginning all scrapers...")
        class_list = class_scraper.get_classes()
        print("Finished scraping classes.")
        building_list = building_scraper.get_buildings()
        print("Finished scraping buildings.")
        library_list = library_scraper.get_libraries()
        print("Finished scraping libraries.")

        cursor.execute('''
        DROP TABLE if EXISTS classes
        ''')
        cursor.execute('''
        CREATE TABLE classes
        (building_num text, class_title text, class_desc text, units text, class_type text, class_subject text, 
        class_number text, facility_id text, day text, start_time text, end_time text, class_duration text)
        ''')
        cursor.execute('''
        DROP TABLE if EXISTS buildings
        ''')
        cursor.execute('''
        CREATE TABLE buildings
        (building_num text, building_name text, building_abbriev text, address text, lat text, lng text)
        ''')
        cursor.execute('''
        DROP TABLE if EXISTS classrooms
        ''')
        cursor.execute('''
        CREATE TABLE classrooms
        (building_num text, facility_id text, building_name text, classroom_number text)
        ''')
        cursor.execute('''
        DROP TABLE if EXISTS libraries
        ''')
        cursor.execute('''
        CREATE TABLE libraries
        (building_num text, library_name text, library_abbriev text, address text, lat text, lng text,
        hours text)
        ''')

        break
    elif (user_input == "class") or (user_input == "c"):
        class_list = class_scraper.get_classes()
        cursor.execute('''
        DROP TABLE if EXISTS classes
        ''')
        cursor.execute('''
        CREATE TABLE classes
        (building_num text, class_title text, class_desc text, units text, class_type text, class_subject text, 
        class_number text, facility_id text, day text, start_time text, end_time text, class_duration text)
        ''')
        break
    elif (user_input == "building") or (user_input == "b"):
        building_list = building_scraper.get_buildings()
        cursor.execute('''
        DROP TABLE if EXISTS buildings
        ''')
        cursor.execute('''
        CREATE TABLE buildings
        (building_num text, building_name text, building_abbriev text, address text, lat text, lng text)
        ''')
        cursor.execute('''
        DROP TABLE if EXISTS classrooms
        ''')
        cursor.execute('''
        CREATE TABLE classrooms
        (building_num text, facility_id text, building_name text, classroom_number text)
        ''')
        break
    elif (user_input == "library") or (user_input == "l"):
        library_list = library_scraper.get_libraries()
        cursor.execute('''
        DROP TABLE if EXISTS libraries
        ''')
        cursor.execute('''
        CREATE TABLE libraries
        (building_num text, library_name text, library_abbriev text, address text, lat text, lng text,
        hours text)
        ''')
        break
    elif (user_input == "exit") or (user_input == "quit") or (user_input == "q"):
        print("Goodbye!")
        break

if (user_input != "exit") and (user_input != "quit") and (user_input != "q"):
    print("Beginning populating database...")

    for meeting in class_list:
        if len(meeting) != 0:
            if local:
                cursor.execute('''
                INSERT INTO classes
                (building_num, class_title, class_desc, units, class_type, class_subject, 
                class_number, facility_id, day, start_time, end_time, class_duration) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', [meeting["Building Number"], meeting["Class Title"], meeting["Class Description"], meeting["Units"],
                      meeting["Class Type"], meeting["Class Subject"], meeting["Class Number"], meeting["Facility ID"],
                      meeting["Day"], meeting["Start Time"], meeting["End Time"], meeting["Duration"]])
            elif not local:
                cursor.execute('''
                INSERT INTO classes
                (building_num, class_title, class_desc, units, class_type, class_subject, 
                class_number, facility_id, day, start_time, end_time, class_duration) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (meeting["Building Number"], meeting["Class Title"], meeting["Class Description"],
                      meeting["Units"],
                      meeting["Class Type"], meeting["Class Subject"], meeting["Class Number"],
                      meeting["Facility ID"],
                      meeting["Day"], meeting["Start Time"], meeting["End Time"], meeting["Duration"]))
    conn.commit()

    for building in building_list:
        if local:
            cursor.execute('''
            INSERT INTO buildings (building_num, building_name, building_abbriev, address, lat, lng)
            VALUES (?, ?, ?, ?, ?, ?)''', [building["buildingNumber"], building["name"], building["buildingCode"],
                                           building["address"], building["latitude"], building["longitude"]])
        elif not local:
            cursor.execute('''
                    INSERT INTO buildings (building_num, building_name, building_abbriev, address, lat, lng)
                    VALUES (%s, %s, %s, %s, %s, %s)''',
                           (building["buildingNumber"], building["name"], building["buildingCode"],
                            building["address"], building["latitude"], building["longitude"]))
        try:
            for classroom in building['classrooms']:
                if local:
                    cursor.execute('''
                        INSERT INTO classrooms (building_num, facility_id, building_name, classroom_number)
                        VALUES (?, ?, ?, ?)''', [building["buildingNumber"], building["buildingCode"] + classroom.zfill(4), building["name"],
                                                 classroom])
                elif not local:
                    cursor.execute('''
                        INSERT INTO classrooms (building_num, facility_id, building_name, classroom_number)
                        VALUES (%s, %s, %s, %s)''', (building["buildingNumber"], building["buildingCode"] + classroom.zfill(4),
                        building["name"], classroom))
        except KeyError as e:
            print("NO CLASSROOMS ERROR")
            print(building)
    conn.commit()

    for library in library_list:
        if local:
            cursor.execute('''
                INSERT INTO libraries (building_num, library_name, library_abbriev, address, lat, lng, hours)
                VALUES (?, ?, ?, ?, ?, ?, ?)''', [library["buildingNumber"], library["title"], library["code"],
                                                  library["address"], library["latitude"], library["longitude"],
                                                  library["hours"]])
        elif not local:
            cursor.execute('''
                INSERT INTO libraries (building_num, library_name, library_abbriev, address, lat, lng, hours)
                VALUES (%s, %s, %s, %s, %s, %s, %s)''', (library["buildingNumber"], library["title"], library["code"],
                                                      library["address"], library["latitude"], library["longitude"],
                                                      library["hours"]))
    conn.commit()

    cursor.close()
    conn.close()

    print("Finished populating database.")