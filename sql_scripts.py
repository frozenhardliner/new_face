import sqlite3, streamlit as st, cv2, face_recognition
import os

conn = sqlite3.connect("worker_database.db")
# Define a function to create and return a database connection
def create_connection(database_name):
    conn = sqlite3.connect(database_name)
    return conn

# Define a function to initialize the database tables if they don't exist
def initialize_database(conn):
    cursor = conn.cursor()
    
    # Create the workers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
               Id  INTEGER PRIMARY KEY AUTOINCREMENT,
               Name TEXT NOT NULL,
               Department TEXT,
               Position TEXT,
               Date_registered DATETIME,
               photo BLOB
        )
    """)

    # Create the registration table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registration (
               Id  INTEGER NOT NULL,
               Date DATE NOT NULL,
               Check_in_dt DATETIME,
               Check_out_dt DATETIME,
               Status TEXT, 
               Check_in_time real,
               Check_out_time real
        )
    """)

    conn.commit()
    cursor.close()

def has_user_checked_in_today(conn ,Id, current_date):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registration where Date = ?  and Id = ?", (current_date,Id ))
    result = cursor.fetchall()
    # If no record is found for today, check if the user ID exists in the table
    if result is None:
        cursor.execute("SELECT * FROM registration WHERE Id = ?", (Id,))
        result = cursor.fetchone()
    cursor.close()
    return True if result != [] else False

def registration_table(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registration")
    registration_data = cursor.fetchall()
    cursor.close()
    return registration_data

def get_worker_ids(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Id FROM workers")
    ids = cursor.fetchall()
    cursor.close()
    return [name[0] for name in ids]

def get_max_id(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Id) FROM workers")
    max_id = cursor.fetchall()
    cursor.close()
    if max_id[0][0] is not None:
        id = max_id[0][0]
    else:
        id = 0
    return id

def worker_info(conn, Id):
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Department, Position from workers where Id = ?", (Id,))
    result = cursor.fetchall()
    cursor.close()
    if result:
        info = {
            "Name": result[0][0],
            "Department": result[0][1],
            "Position": result[0][2]
        }
        return info
    else:
        return None

def show_workers(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Name, Department, Position, Date_registered from workers")
    headers = [description[0] for description in cursor.description]
    workers_db = cursor.fetchall()
    cursor.close()
    return [headers] + workers_db

def delete_worker_table(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workers")
    conn.commit()

    # Remove all photos
    photo_folder = 'visitor_database'
    for file_name in os.listdir(photo_folder):
        file_path = os.path.join(photo_folder, file_name)
        os.remove(file_path)

def load_images_and_classnames():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    visitor_database = os.path.join(root_dir, "visitor_database")
    visitor_history = os.path.join(root_dir, "visitor_history")
    st.session_state['images'] = []
    st.session_state['classnames'] = []
    mylist = os.listdir(visitor_database)
    for photo in mylist:
        current_image = cv2.imread(f'{visitor_database}/{photo}')
        st.session_state.images.append(current_image)
        st.session_state.classnames.append(os.path.splitext(photo)[0])
    return st.session_state.images, st.session_state.classnames

def find_encodings(images):
    st.session_state.encodelist = []
    for index, img in enumerate(images):
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encoded_face = face_recognition.face_encodings(img)[0]
            st.session_state.encodelist.append(encoded_face)
        except:
            print(f"Couldn't recognise photo of index {index}")
    return st.session_state.encodelist

# Create a function to close the database connection
def close_connection(conn):
    conn.close()