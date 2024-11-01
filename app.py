import threading
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
import subprocess
import ffmpeg
import json
import time
import cv2
import torch
from flask import Response
import sqlite3

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# Load YOLOv5 model (you can load any custom-trained model by providing the correct path)
model = torch.hub.load('ultralytics/yolov5', 'custom', path='runs/train/exp/weights/best.pt')


# Initialize Flask app
app = Flask(__name__)

# Define folders for uploads and outputs
UPLOAD_FOLDER = 'uploads/'
OUTPUT_FOLDER = 'runs/detect/'
STATUS_FILE = 'video_status.json'  # File to store video processing status

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure the directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Allowed file types (images and videos)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4'}

lock = threading.Lock()

# Load or initialize the video status file
def load_video_status():
    with lock:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        return {}

# Save the updated status to the JSON file
def save_video_status(status):
    with lock:
        with open(STATUS_FILE, 'w') as f:
            json.dump(status, f)

# Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Background video processing function
def process_video(file_path, output_path, filename):
    ext = filename.rsplit('.', 1)[1].lower()
    video_exts = {'mp4', 'mov', 'avi'}  # Add more video extensions if needed
    image_exts = {'png', 'jpg', 'jpeg'}

    # Update status to processing
    video_status = load_video_status()
    video_status[filename] = {"status": "processing", "path": None, "type": "image" if ext in image_exts else "video"}
    save_video_status(video_status)

    if (ext in video_exts) or (ext in image_exts):
        # Run detect.py for video
        weights = 'runs/train/exp/weights/best.pt'  # Adjust path as necessary
        subprocess.run(['python', 'detect.py', '--weights', weights, '--source', file_path, '--project', 'runs/detect', '--name', 'exp', '--exist-ok'])

    # Update status to processed
    video_status[filename] = {"status": "processed", "path": output_path, "type": "image" if ext in image_exts else "video"}
    save_video_status(video_status)

# Function to convert video format using ffmpeg-python
def convert_video_format(input_path, output_path, format):
    try:
        ffmpeg.input(input_path).output(output_path).run(overwrite_output=True)
    except ffmpeg.Error as e:
        print(f"An error occurred during video conversion: {e}")

# Route for homepage that shows all videos and their status
@app.route('/')
def index():
    video_status = load_video_status()
    return render_template('index.html', videos=video_status)

# Route to handle the file upload and object detection
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Define output path (the resulting video or image)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'exp', filename)
        
        # Start background thread for processing the video
        threading.Thread(target=process_video, args=(file_path, output_path, filename)).start()
        
        # Redirect back to the index page
        return redirect(url_for('index'))

# Route to display the output file
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    video_status = load_video_status()
    if filename in video_status and video_status[filename]["status"] == "processed":
        return send_from_directory(os.path.join(app.config['OUTPUT_FOLDER'], 'exp'), os.path.basename(video_status[filename]["path"]))
    else:
        return "Video is still processing."

@app.route('/get_video_status', methods=['GET'])
def get_video_status():
    video_status = load_video_status()
    return jsonify(video_status)


def init_db():
    conn = sqlite3.connect('objects.db')
    cursor = conn.cursor()
    # Create a table to store detected objects and GPS data if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object_class TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    conn.commit()
    conn.close()

def load_coordinates():
    try:
        with open('address.json', 'r') as f:
            address_data = json.load(f)
            latitude = address_data.get("latitude")
            longitude = address_data.get("longitude")
            return latitude, longitude
    except FileNotFoundError:
        print("address.json file not found.")
        return None, None
    except json.JSONDecodeError:
        print("Error decoding address.json.")
        return None, None

def object_exists(object_class, latitude, longitude):
    conn = sqlite3.connect('objects.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM detections WHERE object_class=? AND latitude=? AND longitude=?",
                   (object_class, latitude, longitude))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def insert_object(object_class, latitude, longitude):
    conn = sqlite3.connect('objects.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO detections (object_class, latitude, longitude) VALUES (?, ?, ?)",
                   (object_class, latitude, longitude))
    conn.commit()
    conn.close()

def gen_frames(camera_index):  
    cap = cv2.VideoCapture(camera_index)  # Capture video from the webcam (index 0 for the default camera)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Perform YOLOv5 inference on the frame
            results = model(frame)  # Pass frame to YOLOv5 model
            
            # Load latitude and longitude from address.json
            latitude, longitude = load_coordinates()
            
            if latitude and longitude:
                # Loop through each detected object in the frame
                for detection in results.xyxy[0]:
                    class_id = int(detection[5])  # Class ID of the detected object
                    label = results.names[class_id]  # Get the label of the detected object
                    
                    # Check if the object and coordinates already exist in the database
                    if not object_exists(label, latitude, longitude):
                        # Insert the new object and coordinates into the database
                        insert_object(label, latitude, longitude)
                        print(f"Inserted into database: {label}, Latitude: {latitude}, Longitude: {longitude}")
                    else:
                        print(f"Object already exists in the database: {label}, Latitude: {latitude}, Longitude: {longitude}")
            
            # Draw bounding boxes on the frame
            frame = results.render()[0]

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Stream the frames to the browser using multipart/x-mixed-replace
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Route to stream the camera input
@app.route('/video_feed/<int:camera>')
def video_feed(camera):
    return Response(gen_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera')
def camera():
    return render_template('camera.html')


def fetch_objects():
    # Connect to the database
    conn = sqlite3.connect('objects.db')
    cur = conn.cursor()

    # Query to fetch all rows from the detected_objects table
    cur.execute("SELECT * FROM detections")
    rows = cur.fetchall()

    # Close the connection to the database
    conn.close()

    return rows

@app.route('/objects')
def display_objects():
    # Fetch the data from the database
    objects = fetch_objects()

    # Render the template and pass the objects to it
    return render_template('objects_table.html', objects=objects)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)