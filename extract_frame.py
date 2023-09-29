import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import subprocess
import numpy as np
import io
from GlobalLink import VideosFolder
import math

def extract_frames_between(video_name, start_frame_idx, end_frame_idx, num_of_res=30):
    # Xác định đường dẫn đến file video
    video_path = os.path.join(VideosFolder, f"{video_name}.mp4")
    print(video_path)

    # Kiểm tra xem file video có tồn tại không
    if not os.path.exists(video_path):
        print(f"File video {video_name} không tồn tại.")
        return None  # Trả về None nếu không thể trích xuất

    # Tạo danh sách idx để lưu các chỉ mục
    frame_indices = []

    # Tạo danh sách để lưu các PhotoImage
    photo_images = []

    # Mở video bằng OpenCV
    cap = cv2.VideoCapture(video_path)

    # Trích xuất các frame trước và sau frame_idx
    interval = math.ceil((end_frame_idx - start_frame_idx) / num_of_res)
    for idx in range(start_frame_idx, end_frame_idx + interval, interval):
        if idx < 0:
            continue
        frame_indices.append(idx)

        # Đặt con trỏ video tới frame cần trích xuất
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)

        # Đọc frame từ video
        ret, frame = cap.read()

        if not ret:
            print(f"Không thể trích xuất frame thứ {idx} từ video {video_name}.")
            continue

        # Chuyển đổi frame thành hình ảnh PIL
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        pil_image = pil_image.resize((160, 90), Image.LANCZOS)
        photo_image = ImageTk.PhotoImage(pil_image)
        photo_images.append(photo_image)

    # Giải phóng tài nguyên video
    cap.release()

    return video_name, frame_indices, photo_images

def extract_frames(video_name,
                    frame_idx, 
                    num_frames_before = 0, 
                    num_frames_after = 0, 
                    frame_stride=1):
    # # Tạo đường dẫn đến thư mục chứa video tương ứng
    # video_folder = os.path.join(videos_folder, 'Videos_' + video_name.split('_')[0], 'video')

    # Xác định đường dẫn đến file video
    video_path = os.path.join(VideosFolder, f"{video_name}.mp4")
    print(video_path)

    # Kiểm tra xem file video có tồn tại không
    if not os.path.exists(video_path):
        print(f"File video {video_name} không tồn tại.")
        return None  # Trả về None nếu không thể trích xuất

    # Tạo danh sách idx để lưu các chỉ mục
    frame_indices = []

    # Tạo danh sách để lưu các PhotoImage
    photo_images = []

    # Mở video bằng OpenCV
    cap = cv2.VideoCapture(video_path)

    # Trích xuất các frame trước và sau frame_idx
    start_idx = frame_idx - num_frames_before*frame_stride
    end_idx = frame_idx + num_frames_after*frame_stride + 1
    for idx in range(start_idx, end_idx, frame_stride):
        if idx < 0:
            continue
        frame_indices.append(idx)

        # Đặt con trỏ video tới frame cần trích xuất
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)

        # Đọc frame từ video
        ret, frame = cap.read()

        if not ret:
            print(f"Không thể trích xuất frame thứ {idx} từ video {video_name}.")
            continue

        # Chuyển đổi frame thành hình ảnh PIL
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        pil_image = pil_image.resize((160, 90), Image.LANCZOS)
        photo_image = ImageTk.PhotoImage(pil_image)
        photo_images.append(photo_image)

    # Giải phóng tài nguyên video
    cap.release()

    return video_name, frame_indices, photo_images