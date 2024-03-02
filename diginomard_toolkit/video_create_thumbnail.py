import os
import sys
import cv2
from PIL import Image, ImageDraw, ImageFont

# output folder
outputDir = "C:/Workspace/Personal/video_photo/output/thumbnail/"
fontPath = "C:/Workspace/Personal/video_photo/fonts/HakgyoansimJiugaeR.ttf"

# Function to generate screenshots of a video file
def generate_screenshots(video_file, output_folder, text, fontSize, interval, intervalOffset):
    # Create output folder if it doesn't exist
    base_file_name = os.path.basename(video_file).split('.')[0]
    output_folder = os.path.join(output_folder, base_file_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the video file
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)

    # Variables for screenshot numbering
    count = 0
    elapsed_time = 0
    wait = False

    # Loop through the video frames
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Check if the elapsed time exceeds the interval
        if not wait and elapsed_time >= intervalOffset:
            wait = True
            # Generate screenshot filename
            screenshot_path = os.path.join(output_folder, f'screenshot_{count}.jpg')

            # Save the frame as an image
            cv2.imwrite(screenshot_path, frame)

            # Add text to the screenshot
            add_text_to_image(screenshot_path, text, fontPath, fontSize)

            count += 1

        if elapsed_time >= frame_interval:
            elapsed_time = 0  # Reset elapsed time
            wait = False

        elapsed_time += 1

    cap.release()

# Function to add text to an image
def add_text_to_image(image_path, text, font_path, font_size=150, font_color='yellow', position=(20, 20)):
    # position bottom left (20,20 is for top left)
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Load font
    font = ImageFont.truetype(font_path, font_size)

    position = 100, image.size[1] - 300

    # Draw text with black stroke
    stroke_width=2
    stroke_color='black'
    for x in range(-stroke_width, stroke_width + 1):
        for y in range(-stroke_width, stroke_width + 1):
            draw.text((position[0] + x, position[1] + y), text, font=font, fill=stroke_color)

    # Add text to image
    draw.text(position, text, font=font, fill=font_color)

    # Save image
    image.save(image_path)


if __name__ == '__main__':
    args = sys.argv
    video_file = args[1]
    text = args[2]
    fontSize = int(args[3])
    generate_screenshots(video_file, outputDir, text, fontSize, 15, 4)

