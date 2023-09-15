import tkinter as tk
from PIL import Image, ImageTk
import os
import subprocess
import numpy as np
import io

def extract_frames(video_name,
                    frame_idx, 
                    num_frames_before = 0, 
                    num_frames_after = 0, 
                    frame_stride=1,  
                    videos_folder = "E:\\AIChallenge\\video"):
    # # Tạo đường dẫn đến thư mục chứa video tương ứng
    # video_folder = os.path.join(videos_folder, 'Videos_' + video_name.split('_')[0], 'video')

    # Xác định đường dẫn đến file video
    video_path = os.path.join(videos_folder, f"\\{video_name}.mp4")

    # Kiểm tra xem file video có tồn tại không
    if not os.path.exists(video_path):
        print(f"File video {video_name} không tồn tại.")
        return None  # Trả về None nếu không thể trích xuất

    # Tạo danh sách để lưu các PhotoImage
    photo_images = []

    # Trích xuất các frame trước và sau frame_idx
    for i in range(frame_idx - num_frames_before*frame_stride, frame_idx + num_frames_after*frame_stride + 1, frame_stride):
        if i < 0:
            continue  # Bỏ qua các frame âm
        # Đọc frame tại vị trí mong muốn từ pipe và chuyển đổi thành hình ảnh PIL
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-vf', f'select=eq(n\,{i})',
            '-vframes', '1',
            '-q:v', '2',
            '-f', 'image2pipe',
            '-c:v', 'png',
            '-pix_fmt', 'rgb24',
            'pipe:1'
        ]

        ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = ffmpeg_process.communicate()
        frame_pil_image = Image.open(io.BytesIO(output))

        # Chuyển đổi frame thành PhotoImage và thêm vào danh sách
        photo_image = ImageTk.PhotoImage(frame_pil_image)
        photo_images.append(photo_image)

    return photo_images


# # Sử dụng hàm
# # Tạo cửa sổ Tkinter
# window = tk.Tk()
# window.title("Hình ảnh từ frame")

# # Sử dụng hàm để trích xuất và hiển thị danh sách các hình ảnh
# video_name = "L03_V001"
# frame_idx = 1000
# videos_folder = "..\Videos"  # Đường dẫn đến thư mục chứa video
# num_frames_before = 5  # Số lượng frame cần xuất phía trước frame_idx
# num_frames_after = 5   # Số lượng frame cần xuất phía sau frame_idx
# frame_stride = 10       # Khoảng cách giữa các frame

# photo_images = extract_frames(video_name, frame_idx, videos_folder, num_frames_before, num_frames_after, frame_stride)

# def display_next_image(index):
#     if index < len(photo_images):
#         label = tk.Label(window, image=photo_images[index])
#         label.pack()
#         window.after(1000, display_next_image, index + 1)  # Hiển thị ảnh tiếp theo sau 1 giây (1000 ms)

# # Bắt đầu hiển thị ảnh đầu tiên
# if photo_images:
#     display_next_image(0)

# # Chạy ứng dụng Tkinter
# window.mainloop()