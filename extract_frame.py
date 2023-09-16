import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import subprocess
import numpy as np
import io
from GlobalLink import VideosFolder

def extract_frames(video_name,
                    frame_idx, 
                    num_frames_before = 0, 
                    num_frames_after = 0, 
                    frame_stride=1,  
                    videos_folder = VideosFolder):
    # # Tạo đường dẫn đến thư mục chứa video tương ứng
    # video_folder = os.path.join(videos_folder, 'Videos_' + video_name.split('_')[0], 'video')

    # Xác định đường dẫn đến file video
    video_path = os.path.join(videos_folder, f"{video_name}.mp4")
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

    return photo_images

    # # Open the video file
    # cap = cv2.VideoCapture(video_path)
    # if not cap.isOpened():
    #     print("Error: Could not open video.")
    #     return

    # # Create a Tkinter window
    # root = tk.Tk()
    # root.title("Video Frames")

    # # Create a canvas for displaying frames
    # canvas = tk.Canvas(root, width=cap.get(cv2.CAP_PROP_FRAME_WIDTH), height=cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # canvas.pack()

    # # Iterate through the frame indices and display each frame
    # for idx in frame_indices:
    #     # Set the video capture position to the desired frame
    #     cap.set(cv2.CAP_PROP_POS_FRAMES, idx)

    #     # Read the frame
    #     ret, frame = cap.read()
    #     if not ret:
    #         print(f"Error: Could not read frame {idx}")
    #         continue

    #     # Convert the frame from BGR to RGB
    #     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #     # Convert the frame to a PIL Image
    #     frame_pil = Image.fromarray(frame_rgb)

    #     # Convert the PIL Image to a PhotoImage object
    #     frame_tk = ImageTk.PhotoImage(frame_pil)

    #     # Display the frame on the canvas
    #     canvas.create_image(0, 0, anchor=tk.NW, image=frame_tk)
    #     canvas.update()  # Update the canvas

    #     # Keep the frame displayed for a short time (adjust as needed)
    #     root.after(1000, lambda: canvas.delete("all"))

    # Close the video file and start the Tkinter main loop
    cap.release()
    root.mainloop()



    # for i in range(start_idx, end_idx, frame_stride):
    #     if i < 0:
    #         continue  # Bỏ qua các frame âm
    #     # Đọc frame tại vị trí mong muốn từ pipe và chuyển đổi thành hình ảnh PIL
    #     cmd = [
    #         'ffmpeg',
    #         '-y',
    #         '-i', video_path,
    #         '-vf', f'select=eq(n\,{i})',
    #         '-vframes', '1',
    #         '-q:v', '2',
    #         '-f', 'image2pipe',
    #         '-c:v', 'png',
    #         '-pix_fmt', 'rgb24',
    #         'pipe:1'
    #     ]

    #     ffmpeg_process = subprocess.Popen(cmd, cwd='D:\\VSCode\\2023-ai-challenge', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     output, _ = ffmpeg_process.communicate()
    #     frame_pil_image = Image.open(io.BytesIO(output))

    #     # Chuyển đổi frame thành PhotoImage và thêm vào danh sách
    #     photo_image = ImageTk.PhotoImage(frame_pil_image)
    #     photo_images.append(photo_image)

    # return photo_images


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