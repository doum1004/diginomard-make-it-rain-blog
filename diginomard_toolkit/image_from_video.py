#pip install opencv-python

import cv2
import os

def extract_images(video_path, output_folder, interval):
    # Open the video file
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print("Error: Unable to open video file.")
        return
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get video properties
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    # Extract images 
    total_frames = int(duration) // interval

    for i in range(total_frames):
        # Calculate frame number for the current time
        frame_number = int(i * interval * fps)
        # Set the frame position
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        # Read the frame
        ret, frame = video.read()
        if not ret:
            print(f"Error: Unable to read frame {i}.")
            continue
        # Save the frame as an image
        image_path = os.path.join(output_folder, f"frame_{i}.jpg")
        cv2.imwrite(image_path, frame)
        print(f"Saved frame {i} as {image_path}")

    # Release the video object
    video.release()
    print("Extraction complete.")

# Example usage
video_path = '/Users/alex.lee/Downloads/test.mp4'
output_folder = '/Users/alex.lee/Downloads/Test'
interval = 10  # seconds
extract_images(video_path, output_folder, interval)