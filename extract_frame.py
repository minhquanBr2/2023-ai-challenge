import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import subprocess
import numpy as np
import io
from GlobalLink import VideosFolder
import math
from frame import VideoFrame
from mapping_keyframe import get_frame_info

def extract_frames_between(video_frame_start, video_frame_end, num_of_res=30):

    video_name = video_frame_start.video_name
    frame_idx_start = int(video_frame_start.frame_idx)
    frame_idx_end = int(video_frame_end.frame_idx)

    results = []

    # Xác định đường dẫn đến file video
    video_path = os.path.join(VideosFolder, f"{video_name}.mp4")
    print(video_path)

    # Kiểm tra xem file video có tồn tại không
    if not os.path.exists(video_path):
        print(f"File video {video_name} không tồn tại.")
        return results  

    # Trích xuất các frame nằm giữa
    interval = math.ceil((frame_idx_end - frame_idx_start) / num_of_res)
    for idx in range(frame_idx_start, frame_idx_end + interval, interval):
        if idx < 0:
            continue
        results.append(VideoFrame("", video_name, "", idx, None, 0))

    return results

def extract_frames_neighbor(videoFrame, num_frames_before=0, num_frames_after=0, frame_stride=1):

    video_name = videoFrame.video_name
    keyframe_idx = videoFrame.keyframe_idx
    frame_idx = videoFrame.frame_idx
    if frame_idx == None:
        frame_idx = get_frame_info(video_name, keyframe_idx)
    frame_idx = int(frame_idx)
    
    results = []

    # Xác định đường dẫn đến file video
    video_path = os.path.join(VideosFolder, f"{video_name}.mp4")
    print(video_path)

    # Kiểm tra xem file video có tồn tại không
    if not os.path.exists(video_path):
        print(f"File video {video_name} không tồn tại.")
        return results  

    # Trích xuất các frame trước và sau frame_idx
    start_idx = frame_idx - num_frames_before * frame_stride
    end_idx = frame_idx + num_frames_after * frame_stride + 1
    for idx in range(start_idx, end_idx, frame_stride):
        if idx < 0:
            continue
        results.append(VideoFrame("", video_name, keyframe_idx, idx, None, 0))

    return results

def extract_photo(video_name, frame_idx):
        
    # Kiểm tra xem file video có tồn tại không
    video_path = os.path.join(VideosFolder, f"{video_name}.mp4")
    if not os.path.exists(video_path):
        print(f"File video {video_name} không tồn tại.")
        return None
    else:
        print(video_path)

    # Mở video bằng OpenCV
    cap = cv2.VideoCapture(video_path)

    # Đặt con trỏ video tới frame cần trích xuất
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

    # Đọc frame từ video
    ret, frame = cap.read()

    if not ret:
        print(f"Không thể trích xuất frame thứ {frame_idx} từ video {video_name}.")
        return None

    # Chuyển đổi frame thành hình ảnh PIL
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    pil_image = pil_image.resize((160, 90), Image.LANCZOS)
    photo = ImageTk.PhotoImage(pil_image)

    # Giải phóng tài nguyên video
    cap.release()

    return photo


