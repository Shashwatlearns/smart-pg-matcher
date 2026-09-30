import os
import sqlite3
import json

# Absolute path: the database file always sits next to this file.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pg_matcher.db")


def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DB_PATH):
    """Builds both tables from scratch and fills them with sample data."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # DROP first so an older table layout never causes a mismatch
    cursor.execute("DROP TABLE IF EXISTS students")
    cursor.execute("DROP TABLE IF EXISTS pgs")

    cursor.execute('''
        CREATE TABLE students (
            id TEXT PRIMARY KEY,
            name TEXT,
            budget REAL,
            preferred_area TEXT,
            max_distance_km REAL,
            food_pref TEXT,
            sleep_schedule TEXT,
            habits_set TEXT,
            amenities_set TEXT,
            current_pg_id TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE pgs (
            id TEXT PRIMARY KEY,
            name TEXT,
            rent REAL,
            area TEXT,
            distance_km REAL,
            food_offered TEXT,
            ac_available BOOLEAN,
            amenities_set TEXT
        )
    ''')

    pgs_data = [
        ("PG01", "Sunrise Stays", 12000, "Wakad", 3.5, "Any", True, json.dumps(["WiFi", "Gym", "Washing Machine"])),
        ("PG02", "Hinjewadi Hub", 8000, "Hinjewadi", 1.2, "Veg", False, json.dumps(["WiFi", "Power Backup"])),
        ("PG03", "Viman Nagar Villas", 18000, "Viman Nagar", 4.0, "Any", True, json.dumps(["WiFi", "Gym", "Pool", "Washing Machine"])),
        ("PG04", "Kothrud Comforts", 11000, "Kothrud", 2.0, "Veg", False, json.dumps(["WiFi", "Library"])),
        ("PG05", "Baner Bliss", 15000, "Baner", 2.5, "Any", True, json.dumps(["WiFi", "Gym", "Power Backup"])),
        ("PG06", "Tech Park Inn", 9500, "Hinjewadi", 0.8, "Any", False, json.dumps(["WiFi", "Washing Machine"])),
        ("PG07", "Wakad Premium", 14000, "Wakad", 4.2, "Veg", True, json.dumps(["WiFi", "Gym", "Power Backup"])),
        ("PG08", "Airport View", 16500, "Viman Nagar", 5.5, "Any", True, json.dumps(["WiFi", "Washing Machine"])),
        ("PG09", "Student Square", 7500, "Kothrud", 1.5, "Veg", False, json.dumps(["Library"])),
        ("PG10", "Baner Heights", 17000, "Baner", 3.0, "Any", True, json.dumps(["WiFi", "Gym", "Pool"])),
        ("PG11", "Hinjewadi Phase 2 Nest", 10000, "Hinjewadi", 2.0, "Veg", True, json.dumps(["WiFi"])),
        ("PG12", "Wakad Woods", 13000, "Wakad", 5.0, "Any", False, json.dumps(["WiFi", "Washing Machine", "Power Backup"])),
        ("PG13", "Viman Elite", 20000, "Viman Nagar", 3.2, "Any", True, json.dumps(["WiFi", "Gym", "Pool", "Washing Machine"])),
        ("PG14", "Kothrud Central", 12500, "Kothrud", 0.5, "Veg", True, json.dumps(["WiFi", "Power Backup"])),
        ("PG15", "Baner Co-living", 15500, "Baner", 1.8, "Any", True, json.dumps(["WiFi", "Gym", "Washing Machine"])),
    ]

    # The last value in each row is the PG the student already lives in
    students_data = [
        ("S01", "Aarav Patil", 15000, "Baner", 3.0, "Any", "Night Owl", json.dumps(["gaming", "studying_late"]), json.dumps(["WiFi", "Gym"]), "PG05"),
        ("S02", "Neha Sharma", 12000, "Wakad", 5.0, "Veg", "Early Bird", json.dumps(["yoga", "reading"]), json.dumps(["WiFi", "Washing Machine"]), "PG01"),
        ("S03", "Rohan Joshi", 10000, "Hinjewadi", 2.0, "Any", "Flexible", json.dumps([]), json.dumps(["WiFi"]), "PG02"),
        ("S04", "Priya Deshmukh", 18000, "Viman Nagar", 6.0, "Any", "Night Owl", json.dumps(["music"]), json.dumps(["WiFi", "Gym", "Pool"]), "PG03"),
        ("S05", "Aditya Kulkarni", 11000, "Kothrud", 3.0, "Veg", "Early Bird", json.dumps(["studying"]), json.dumps(["Library", "WiFi"]), "PG04"),
        ("S06", "Sneha Iyer", 16000, "Baner", 4.0, "Veg", "Flexible", json.dumps(["cooking"]), json.dumps(["WiFi", "Washing Machine", "Power Backup"]), "PG10"),
        ("S07", "Vikram Singh", 9000, "Hinjewadi", 1.5, "Any", "Night Owl", json.dumps(["gaming"]), json.dumps(["WiFi"]), "PG06"),
        ("S08", "Pooja Nair", 14000, "Wakad", 4.5, "Any", "Early Bird", json.dumps(["fitness"]), json.dumps(["WiFi", "Gym"]), "PG07"),
        ("S09", "Karan Mehta", 20000, "Viman Nagar", 5.0, "Any", "Night Owl", json.dumps(["partying", "music"]), json.dumps(["WiFi", "AC", "Pool"]), "PG13"),
        ("S10", "Anjali Rao", 13000, "Kothrud", 2.5, "Veg", "Flexible", json.dumps(["reading"]), json.dumps(["WiFi", "Power Backup"]), "PG14"),
    ]

    cursor.executemany("INSERT INTO pgs VALUES (?, ?, ?, ?, ?, ?, ?, ?)", pgs_data)
    cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", students_data)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def ensure_db(db_path=DB_PATH):
    """
    Builds the database if it is missing, empty, or uses the old layout
    (no current_pg_id column). Otherwise leaves your saved data alone.
    """
    if not os.path.exists(db_path):
        init_db(db_path)
        return

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('students', 'pgs')"
    )
    found_tables = cursor.fetchall()

    has_new_column = False
    if len(found_tables) == 2:
        cursor.execute("PRAGMA table_info(students)")
        column_names = [row["name"] for row in cursor.fetchall()]
        has_new_column = "current_pg_id" in column_names

    conn.close()

    if len(found_tables) < 2 or not has_new_column:
        init_db(db_path)


def _next_id(cursor, table_name, prefix):
    """Finds the highest number used so far (like PG15) and returns the next id (PG16)."""
    cursor.execute(f"SELECT id FROM {table_name}")
    highest_number = 0
    for row in cursor.fetchall():
        row_id = row["id"]
        number_part = row_id[len(prefix):]
        if row_id.startswith(prefix) and number_part.isdigit():
            highest_number = max(highest_number, int(number_part))
    return f"{prefix}{highest_number + 1:02d}"


def add_pg(pg_data: dict, db_path=DB_PATH) -> dict:
    """Saves a new PG and returns it (with its new id) in the same shape get_all_pgs uses."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    new_id = _next_id(cursor, "pgs", "PG")
    amenities_list = sorted(pg_data["amenities_set"])

    cursor.execute(
        "INSERT INTO pgs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            new_id,
            pg_data["name"],
            pg_data["rent"],
            pg_data["area"],
            pg_data["distance_km"],
            pg_data["food_offered"],
            int(pg_data["ac_available"]),
            json.dumps(amenities_list),
        ),
    )
    conn.commit()
    conn.close()

    saved_pg = dict(pg_data)
    saved_pg["id"] = new_id
    saved_pg["ac_available"] = bool(pg_data["ac_available"])
    saved_pg["amenities_set"] = set(amenities_list)
    return saved_pg


def add_student(student_data: dict, db_path=DB_PATH) -> dict:
    """Saves a new student and returns them (with their new id)."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    new_id = _next_id(cursor, "students", "S")
    habits_list = sorted(student_data["habits_set"])
    amenities_list = sorted(student_data["amenities_set"])

    cursor.execute(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            new_id,
            student_data["name"],
            student_data["budget"],
            student_data["preferred_area"],
            student_data["max_distance_km"],
            student_data["food_pref"],
            student_data["sleep_schedule"],
            json.dumps(habits_list),
            json.dumps(amenities_list),
            student_data.get("current_pg_id"),
        ),
    )
    conn.commit()
    conn.close()

    saved_student = dict(student_data)
    saved_student["id"] = new_id
    saved_student["habits_set"] = set(habits_list)
    saved_student["amenities_set"] = set(amenities_list)
    saved_student["current_pg_id"] = student_data.get("current_pg_id")
    return saved_student


def get_all_pgs(db_path=DB_PATH):
    """Fetches all PGs as a list of dictionaries."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pgs")
    rows = cursor.fetchall()
    conn.close()

    pgs = []
    for row in rows:
        pg = dict(row)
        pg['ac_available'] = bool(pg['ac_available'])
        pg['amenities_set'] = set(json.loads(pg['amenities_set']))
        pgs.append(pg)
    return pgs


def get_all_students(db_path=DB_PATH):
    """Fetches all students as a list of dictionaries."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()

    students = []
    for row in rows:
        student = dict(row)
        student['habits_set'] = set(json.loads(student['habits_set']))
        student['amenities_set'] = set(json.loads(student['amenities_set']))
        students.append(student)
    return students


if __name__ == "__main__":
    init_db()