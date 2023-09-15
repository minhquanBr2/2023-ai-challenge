import os

# Given directory string
directory_string = r"E:\\AIChallenge\\Keyframes\\L01_V001\\0001.jpg"

# Split the string into components
parts = directory_string.split(os.sep)
print(parts)
# Extract the video name and frame name
video_name = parts[-3]
frame_name_with_extension = parts[-1]

# Remove the file extension to get the frame name without extension
frame_name = os.path.splitext(frame_name_with_extension)[0]

# Print the extracted values
print("Video Name:", video_name)
print("Frame Name:", frame_name)
