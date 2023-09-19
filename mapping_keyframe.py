import os
import csv
from GlobalLink import CsvFolder

def parse_direc(path):
    # Given directory string
    directory_string = path
    # Split the string into components
    parts = directory_string.split(os.sep)

    # Extract the video name and frame name
    video_name = parts[-2]
    frame_name_with_extension = parts[-1]

    # Remove the file extension to get the frame name without extension
    frame_name = os.path.splitext(frame_name_with_extension)[0]

    # Print the extracted values
    return {
        "video_name" : video_name,
        "kframe" : int(frame_name)
    }
    # print("Video Name:", video_name)
    # print("Frame Name:", frame_name)

def get_frame_info(video_name, keyframe_name, csv_folder = CsvFolder):
    # Xác định tên file CSV tương ứng với video
    csv_file_name = f"{video_name}.csv"
    csv_file_path = os.path.join(csv_folder, csv_file_name)
    
    if not os.path.exists(csv_file_path):
        return None  # File CSV không tồn tại cho video này
    
    # Đọc thông tin từ file CSV
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            frame_idx = int(row['n'])
            keyframe_file_idx = int(keyframe_name)
            
            if frame_idx == keyframe_file_idx:
                return {
                    'frame_idx': int(row['frame_idx']),
                    # 'pts_time': float(row['pts_time'])
                }

    return None  # Không tìm thấy thông tin cho keyframe này

# # Sử dụng hàm
# video_name = "L01_V001"
# keyframe_name = 5
# csv_folder = "E:\\2023 HCM AI CHALLENGE\\map-keyframes"
# frame_info = get_frame_info(video_name, keyframe_name, csv_folder)

# if frame_info is not None:
#     print(f"Video: {video_name}, Keyframe: {keyframe_name}")
#     print(f"frame_idx: {frame_info['frame_idx']}")
#     # print(f"pts_time: {frame_info['pts_time']}")
# else:
#     print(f"Không tìm thấy thông tin cho Video: {video_name}, Keyframe: {keyframe_name}")
