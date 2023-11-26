import streamlit as st, pandas as pd
from datetime import datetime
import sqlite3, os, time
from sql_scripts import *
from image_loader import *
#from app import load_images_and_classnames, find_encodings
from streamlit_option_menu import option_menu
conn = sqlite3.connect("worker_database.db")
st.set_page_config(
     page_title="User Database",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded")
st.write("<h1 class='title'>Worker Management Database</h1>", unsafe_allow_html=True) 
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)  

with st.sidebar:
    selected = option_menu("Main Menu", ["Database", 'Report'], 
        icons=['house', 'gear'], menu_icon="cast", default_index=0)
#col1, col2 = st.columns(2)
col1, col2, col3 = st.columns([2,1,1])
def database_table():
    with col1:
        query_name = st.text_input("Filter database")

        worker_data = show_workers(conn)
        df = pd.DataFrame(worker_data[1:], columns=worker_data[0])
        if query_name:
            mask = df.applymap(lambda x: query_name.lower().strip() in str(x).lower().strip()).any(axis=1)
            df = df[mask]
        # Apply basic styling to the DataFrame using the 'styler' parameter
        st.data_editor(df.style
            .set_properties(**{'font-size': '16px', 'text-align': 'center'})
            .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
        , hide_index=True, width=800, height=300) 
if selected == "Database":  
    database_table()
    with col3:
        selected_worker = st.selectbox("Select worker to remove", get_worker_ids(conn))
        if st.button("Remove worker by ID",type= 'primary'):
            # Remove worker from db
            photo_path = os.path.join('visitor_database', f'{get_max_id(conn)}.jpg')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workers WHERE id = ?", (selected_worker,))
            conn.commit()
            try:
                os.remove(photo_path)
            except OSError:
                pass
            st.success(f'Removed worker: {selected_worker}')
            load_images_and_classnames()
            find_encodings(st.session_state.images)
            st.rerun()
        if st.toggle("Remove whole database"):
            st.info("Are you sure?")
            if st.button("Yes"):
                delete_worker_table(conn)
                st.rerun()

    with col2:
        new_worker_name = st.text_input("Worker Name:", '')
        department = st.text_input("Department:", '')
        position = st.text_input("Position:", '')
        allowed_image_type = ["jpg", "png", "jpeg"]
        photo_source = st.radio("Photo", options= ["Upload from a desktop", "Take a photo"])
        photo_byte = None
    with col1:
        if photo_source == "Upload from a desktop":
            new_worker_photo = st.file_uploader("Upload Worker Photo (jpg/png/jpeg)", type = allowed_image_type)
            if new_worker_photo is not None:
                photo_byte = new_worker_photo.getvalue()
        elif photo_source == "Take a photo":
            new_worker_photo = st.camera_input("Take a picture")
            if new_worker_photo is not None:
                photo_byte = new_worker_photo.getvalue()
        if len(new_worker_name)>0 and photo_byte is not None:
            with col2:
                if st.button("Add Worker"):
                    face_number = find_face(new_worker_photo)
                    if face_number == 1:
                        current_datetime = datetime.now()
                        conn = sqlite3.connect("worker_database.db")
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO workers (Name, Department, Position, Date_registered, photo) VALUES (?,?,?,?,?)",
                            ( new_worker_name, department, position, current_datetime, photo_byte))
                        conn.commit()
                        with open(os.path.join('visitor_database', f'{get_max_id(conn)}.jpg'), 'wb') as file:
                            file.write(new_worker_photo.getbuffer())
                        # Display success message
                        success_message = st.success('Image and worker information saved successfully!')
                        st.success(f'Added new worker: {new_worker_name}, Id is: {get_max_id(conn)}')
                        # Remove success message after 2 seconds
                        time.sleep(1)
                        success_message.empty()
                        load_images_and_classnames()
                        st.rerun() 
if selected == 'Report':
    st.write("Hello")
