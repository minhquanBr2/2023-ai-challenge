import os
import csv
from GlobalLink import CsvFolder

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
                return row['frame_idx']

    return None  # Không tìm thấy thông tin cho keyframe này
