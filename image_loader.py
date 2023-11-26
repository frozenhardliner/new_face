import os
import cv2
import face_recognition
import streamlit as st
import numpy as np

root_dir = os.path.dirname(os.path.abspath(__file__))
visitor_database = os.path.join(root_dir, "visitor_database")
visitor_history = os.path.join(root_dir, "visitor_history")

images = []
classnames = []
encodelist = []
def find_face(new_worker_photo):
    bytes_data = new_worker_photo.getvalue()
    image = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    img = cv2.resize(image, (0, 0), None, 0.25, 0.25)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Detect face locations in the image
    face_locations = face_recognition.face_locations(img)
    face_number = len(face_locations)
    if len(face_locations) == 1:
        # Draw rectangles around detected faces
        for face_location in face_locations:
            y1, x2, y2, x1 = face_location
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(image, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
        
        # Display the image with detected faces
        st.image(image, channels="BGR", use_column_width=True)
        return face_number
    elif len(face_locations) != 1:
        st.write(" :confused: No faces detected in the photo or more than 1 faces are found.")  
        return face_number
# def load_images_and_classnames():
#     images = []
#     classnames = []
#     encodelist = []
#     mylist = os.listdir(visitor_database)
#     for photo in mylist:
#         current_image = cv2.imread(os.path.join(visitor_database, photo))
#         images.append(current_image)
#         classnames.append(os.path.splitext(photo)[0])
#         img = cv2.cvtColor(current_image, cv2.COLOR_RGB2BGR)
#         encoded_face = face_recognition.face_encodings(img)[0]
#         encodelist.append(encoded_face)
#     return images, classnames, encodelist
def load_new_image(image):
    current_image = cv2.imread(image)
    try:
        img = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
        encoded_face = face_recognition.face_encodings(img)[0]
        encodelist.append(encoded_face)
        images.append(current_image)
        classnames.append(os.path.splitext(os.path.basename(image))[0])
    except:
        st.write("Couldn't recognise face of employee, try 1 more time please")
def remove_image(Id):
    position = classnames.index(str(Id))
    classnames.pop(position)
    images.pop(position)
    encodelist.pop(position)






# Example of how to use the function:
#images, classnames, encodelist = load_images_and_classnames()
print("Loaded", len(images), "images and", len(classnames), "classnames.", len(encodelist), "encodings")