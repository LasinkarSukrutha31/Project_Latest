from flask import Flask, render_template, request, redirect, url_for
import cv2
import os
import numpy as np

# Create a Flask app with the template folder set to the current directory
app = Flask(__name__, template_folder='.')

# Path for uploaded images
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Haar cascade for face detection (pre-trained model)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Store registered face encodings (in-memory for now)
registered_faces = {}

# Home route
@app.route('/')
def home():
    return render_template('welcome.html')

# Registration route
@app.route('/register')
def register():
    return render_template('reg2.html')

# Handle the registration form submission
@app.route('/submit_registration', methods=['POST'])
def submit_registration():
    aadhar = request.form['aadhar']
    face_image = request.files['faceImage']

    # Save the uploaded image
    image_path = os.path.join(UPLOAD_FOLDER, face_image.filename)
    face_image.save(image_path)

    # Process the image to detect faces
    detected_face = detect_face(image_path)

    # If a face is detected, save the data
    if detected_face:
        registered_faces[aadhar] = face_image.filename  # Store registered face by Aadhar number
        with open('register_faces_data.csv', 'a') as file:
            file.write(f"{aadhar},{face_image.filename},Face Detected\n")
        return redirect(url_for('home'))  # Redirect to home page after successful registration
    else:
        return "No face detected, please try again with a clearer image.", 400

# Voting route
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        vote_image = request.files['voteImage']
        
        # Save the uploaded vote image
        image_path = os.path.join(UPLOAD_FOLDER, vote_image.filename)
        vote_image.save(image_path)

        # Process the image to detect and match the face
        detected_face = detect_face(image_path)

        if detected_face:
            aadhar = find_matching_face(detected_face)  # Find the Aadhar of the matched face
            if aadhar:
                return f"Vote Successful! Your Aadhar: {aadhar}"
            else:
                return "No matching face detected. Please try again.", 400
        else:
            return "No face detected in the voting image.", 400

    return render_template('vote.html')

# Function to detect face in the uploaded image
def detect_face(image_path):
    # Read the image using OpenCV
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return None  # No face detected
    else:
        for (x, y, w, h) in faces:
            # Draw a rectangle around the face
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Save the image with the detected face
        face_detected_image_path = os.path.join(UPLOAD_FOLDER, 'detected_' + os.path.basename(image_path))
        cv2.imwrite(face_detected_image_path, img)

        # Return path of the detected face image for further comparison
        return face_detected_image_path

# Function to find the registered face that matches the detected one
def find_matching_face(detected_image_path):
    # Here you can compare the detected image with the stored images
    # In a simple case, you can use a basic method like comparing histograms or face embeddings
    for aadhar, face_filename in registered_faces.items():
        # For now, simply check if the file matches (you can add better face recognition here)
        if detected_image_path.endswith(face_filename):
            return aadhar  # Found a match based on filename for simplicity
    
    return None  # No match found

if __name__ == '__main__':
    app.run(debug=True, port=5004)
