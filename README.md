# Roadside Rubbish Detection Application - User Guide

## Overview

The Roadside Rubbish Detection App is an AI-powered tool designed to help local councils and environmental services detect and manage rubbish from uploaded videos, photos, and real-time video feeds. By utilizing YOLOv5, a state-of-the-art object detection model, the app identifies and categorizes rubbish items, providing location tags for efficient management and reporting.

## Key Features

-   **Image/Video Upload & Detection**: Users can upload photos or videos, and the app will process them to detect and label rubbish items.

-   **Real-Time Detection Feed**: The app also supports live video feeds, detecting objects in real time with bounding boxes and labels.

-   **Location Tagging**: Detected items are stored with location information to assist in waste management.

-   **Database Logging**: Each detected object is saved in a database with its label and location, enabling tracking and analysis.

## How to Use

### 1. Home Page - Uploading Files

-   **Step 1**: Open the application and go to the home page.

-   **Step 2**: Click the "Upload" button to select a photo or video file from your device.

-   **Accepted Formats**: The app accepts `.jpg`, `.jpeg`, `.png` for images and `.mp4` for videos.

-   **Step 3**: After uploading, the app will begin processing the file in the background. Processing status is displayed on the home page.

### 2. Viewing Detection Results

-   Once processing completes, detected items will appear with bounding boxes and labels in the output image/video.

-   For video files, playback controls allow you to pause, fast-forward, and rewind the processed video.

### 3. Real-Time Detection Feed

-   **Step 1**: Navigate to the **Live Feed** tab.

-   **Step 2**: Start the live feed by selecting a camera source (e.g., webcam).

-   **Step 3**: Detected items will be displayed on the video feed in real time with bounding boxes and labels.

### 4. Object and Location Database

-   **View Records**: The app maintains a record of detected items, each with its category and GPS-based mock location data. You can access the **Database** tab to view this data.

-   **Search & Filter**: Use the built-in search feature to find specific items by label or location.

## Example Inputs and Outputs

-   **Sample Input**: Upload a photo of roadside trash, such as a couch and plastic bottles, or a video of a roadside scene.

-   **Expected Output**: The app will display bounding boxes around each detected item (e.g., "Couch" and "Plastic Bottle") and save the detection to the database with a location tag.

## System Requirements

-   The application requires a web browser to access the interface.

-   Ensure your device has a functioning camera for real-time feed usage.

## Troubleshooting

-   If uploads do not process, ensure the file format is supported and try reloading the page.

-   If the live feed is unavailable, confirm camera permissions are enabled in your browser settings.

