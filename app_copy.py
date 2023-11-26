import streamlit as st, sqlite3, pandas as pd, numpy as np
import time, os
from datetime import datetime
import cv2
import face_recognition
from sql_scripts import *
from image_loader import *

st.set_page_config(
     page_title="Face Detection App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)  


conn = sqlite3.connect("worker_database.db")
cursor = conn.cursor()
# Create table if does not exists
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
conn.commit()


if 'images' not in st.session_state:
    st.session_state['images'] = []
if 'classnames' not in st.session_state:
    st.session_state['classnames'] = []
if 'encodelist' not in st.session_state:
    st.session_state.encodelist = []
if st.session_state['images'] == []:
    load_images_and_classnames()
    find_encodings(st.session_state.images)

st.markdown("<h1 class='title'>Video Monitoring</h1>", unsafe_allow_html=True) 
name = None
col1,col2,col3 = st.columns([5,1,1])
with col1:
    img_file_buffer = st.camera_input("")
    if img_file_buffer is not None:
        encoded_face_train = st.session_state.encodelist
        img_file_buffer = cv2.imdecode(np.frombuffer(img_file_buffer.read(), np.uint8), cv2.IMREAD_COLOR) 
        imgs = cv2.resize(img_file_buffer, (0, 0), None, 0.25, 0.25)
        imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)
        face_in_frame = face_recognition.face_locations(imgs)
        encode_face = face_recognition.face_encodings(imgs, face_in_frame)
        for encode_face, faceloc in zip(encode_face, face_in_frame):
            matches = face_recognition.compare_faces(encoded_face_train, encode_face)
            faceDist = face_recognition.face_distance(encoded_face_train, encode_face)
            matchIndex = np.argmin(faceDist)
            print(matchIndex)
            if matches[matchIndex]:
                name = int(st.session_state.classnames[matchIndex].upper().lower())
                name = worker_info(name)["Name"]
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img_file_buffer, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img_file_buffer, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img_file_buffer, name, (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)        
        # Display the recognized image with highlighted faces
        if name:
            current_time = datetime.now()
            col1.image(img_file_buffer, caption=f"Have a nice day, {name}", channels='BGR', use_column_width=True)
            col2.markdown(f"**Worker Name:**\n{name}")
            col2.markdown(f"**Time Now:**\n{current_time.strftime('%Y-%m-%d %H:%M:%S')}")
