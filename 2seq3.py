import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

import fiftyone as fo
import fiftyone.brain as fob
import fiftyone.zoo as foz
from fiftyone import ViewField as F
import numpy as np
from glob import glob
import json
import os
import csv

import heapq
from mapping_keyframe import get_frame_info
from extract_frame import extract_frames_between, extract_frames_neighbor, extract_photo
from GlobalLink import KeyframeFolder, ResultsCSV, VideosFolder, BrainKey, DatasetName
from ocr.search.whoosh_search import search_text_ocr, search_text_subtitle

import subprocess

from frame import VideoFrame


def extract_video_frame_from_path(file_path):
    # Split the file path using backslashes as the delimiter
    parts = file_path.split('\\')

    # Check if the path contains at least 5 parts
    if len(parts) >= 5:
        video_name = parts[-2]  # The video name is the third-to-last part
        frame_number = parts[-1].split('.')[0]  # Remove the file extension

        return {
            'video': video_name,
            'frame': frame_number
        }
    else:
        return None

def text_to_list(text):
    list = text.split(',')
    cleaned_list = [chunk.strip() for chunk in list]
    return cleaned_list

def text_to_list(text):
    list = text.split(',')
    cleaned_list = [chunk.strip() for chunk in list]
    return cleaned_list

class ImageApp:

    def on_canvas_configure(self, event):
        self.image_display_a_canvas.configure(scrollregion=self.image_display_a_canvas.bbox("all"))
        self.image_display_b_canvas.configure(scrollregion=self.image_display_b_canvas.bbox("all"))

    def __init__(self, root, dataset):
        self.root = root
        self.dataset = dataset
        self.timeline_labels = []
        self.root.title("Image Viewer")
        self.view_a = None
        self.view_b = None
        
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        self.framewidth_unit = int(self.screenwidth / 9 * 0.9)

        # FOR INPUT
        # ở đây ta có 2 frame ở vị trí top, mỗi frame ứng với 1 dòng label + 1 ô nhập text + 1 nút search
        self.sequence_a_frame = tk.Frame(self.root)
        self.sequence_a_frame.pack(side="top", anchor="w")
        
        self.sequence_ocr_a_frame = tk.Frame(self.root)
        self.sequence_ocr_a_frame.pack(side="top", anchor="w")
        
        self.sequence_subtitle_a_frame = tk.Frame(self.root)
        self.sequence_subtitle_a_frame.pack(side="top", anchor="w")

        self.sequence_b_frame = tk.Frame(self.root)
        self.sequence_b_frame.pack(side="top", anchor="w")

        self.sequence_ocr_b_frame = tk.Frame(self.root)
        self.sequence_ocr_b_frame.pack(side="top", anchor="w")
        
        self.sequence_subtitle_b_frame = tk.Frame(self.root)
        self.sequence_subtitle_b_frame.pack(side="top", anchor="w")

        # info_display: frame dùng để hiển thị thông tin của frame đã chọn
        self.info_display = tk.Frame(self.root)
        self.info_display.pack(side = "top")

        # SELECTED IMAGE: các biến lưu path các ảnh được chọn
        self.selected_video_frame_a = None
        self.selected_video_frame_b = None
        self.selected_video_frame_c = (None, None)
        self.selected_video_frame_d = None
        self.result_video_frames_a = []
        self.result_video_frames_b = []
        self.result_video_frames_c = []
        self.result_video_frames_d = []

        # image_display: là cái frame được dùng như grid để bố trí các thành phần trên cửa sổ
        self.image_display = tk.Frame(self.root)
        self.image_display.pack(side="bottom", padx=10)

        self.image_display_a = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500)
        self.image_display_a.grid(row=0, column=0, columnspan=2)

        self.image_display_b = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500)
        self.image_display_b.grid(row=0, column=2, columnspan=2)
        
        self.image_display_c = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500)
        self.image_display_c.grid(row=0, column=4, columnspan=2)

        self.image_display_d = tk.Frame(self.image_display, width=3*self.framewidth_unit, height=500)
        self.image_display_d.grid(row=0, column=6, columnspan=2)


        # 6 search buttons at the bottom
        self.search_a_prev_button = tk.Button(self.image_display, text="Search prev of A", command=lambda: self.search_prev(self.selected_video_frame_a))
        self.search_a_prev_button.grid(row=1, column=0, sticky=tk.E)

        self.search_a_next_button = tk.Button(self.image_display, text="Search next of A", command=lambda: self.search_next(self.selected_video_frame_a))
        self.search_a_next_button.grid(row=1, column=1, sticky=tk.W)
    
        self.search_b_prev_button = tk.Button(self.image_display, text="Search prev of B", command=lambda: self.search_prev(self.selected_video_frame_b))
        self.search_b_prev_button.grid(row=1, column=2, sticky=tk.E)
    
        self.search_b_next_button = tk.Button(self.image_display, text="Search next of B", command=lambda: self.search_next(self.selected_video_frame_b))
        self.search_b_next_button.grid(row=1, column=3, sticky=tk.W)

        self.search_pair_ab_button = tk.Button(self.image_display, text="Search pair A-B", command=lambda: self.search_pair('ab'))
        self.search_pair_ab_button.grid(row=1, column=4, sticky=tk.E)

        self.search_pair_ba_button = tk.Button(self.image_display, text="Search pair B-A", command=lambda: self.search_pair('ba'))
        self.search_pair_ba_button.grid(row=1, column=5, sticky=tk.W)

        


        # FOR IMAGE DISPLAYING
        self.image_display_a_canvas = tk.Canvas(self.image_display_a, width=2*self.framewidth_unit, height=500)
        self.image_display_a_canvas.pack(side="left", fill="both", expand=True)

        self.image_display_b_canvas = tk.Canvas(self.image_display_b, width=2*self.framewidth_unit, height=500)
        self.image_display_b_canvas.pack(side="left", fill="both", expand=True)

        self.image_display_c_canvas = tk.Canvas(self.image_display_c, width=2*self.framewidth_unit, height=500)
        self.image_display_c_canvas.pack(side="left", fill="both", expand=True)

        self.image_display_d_canvas = tk.Canvas(self.image_display_d, width=3*self.framewidth_unit, height=500)
        self.image_display_d_canvas.pack(side="left", fill="both", expand=True)

        # Create a Scrollbar for the Canvas
        self.scrollbar_a = tk.Scrollbar(self.image_display_a, orient="vertical", command=self.image_display_a_canvas.yview)
        self.scrollbar_a.pack(side="right", fill="y")
        
        self.scrollbar_b = tk.Scrollbar(self.image_display_b, orient="vertical", command=self.image_display_b_canvas.yview)
        self.scrollbar_b.pack(side="right", fill="y")
        
        self.scrollbar_c = tk.Scrollbar(self.image_display_c, orient="vertical", command=self.image_display_c_canvas.yview)
        self.scrollbar_c.pack(side="right", fill="y")

        self.scrollbar_d = tk.Scrollbar(self.image_display_d, orient="vertical", command=self.image_display_d_canvas.yview)
        self.scrollbar_d.pack(side="right", fill="y")

        # Configure the Canvas to use the Scrollbar
        self.image_display_a_canvas.configure(yscrollcommand=self.scrollbar_a.set)
        self.image_display_b_canvas.configure(yscrollcommand=self.scrollbar_b.set)
        self.image_display_c_canvas.configure(yscrollcommand=self.scrollbar_c.set)
        self.image_display_d_canvas.configure(yscrollcommand=self.scrollbar_d.set)

        # Create a Frame inside the Canvas to hold the Label
        self.image_display_a_frame = tk.Frame(self.image_display_a_canvas)
        self.image_display_a_canvas.create_window((0, 0), window=self.image_display_a_frame, anchor="nw")
        self.image_display_b_frame = tk.Frame(self.image_display_b_canvas)
        self.image_display_b_canvas.create_window((0, 0), window=self.image_display_b_frame, anchor="nw")
        self.image_display_c_frame = tk.Frame(self.image_display_c_canvas)
        self.image_display_c_canvas.create_window((0, 0), window=self.image_display_c_frame, anchor="nw")
        self.image_display_d_frame = tk.Frame(self.image_display_d_canvas)
        self.image_display_d_canvas.create_window((0, 0), window=self.image_display_d_frame, anchor="nw")

        # Bind the canvas to a function that updates scroll region
        # self.image_display_canvas.bind("<Configure>", self.on_canvas_configure)

        self.image_display_a_frame.update()
        self.image_display_a_canvas.configure(scrollregion=self.image_display_a_canvas.bbox('all'))
        
        self.image_display_b_frame.update()
        self.image_display_b_canvas.configure(scrollregion=self.image_display_b_canvas.bbox('all'))

        self.image_display_c_frame.update()
        self.image_display_c_canvas.configure(scrollregion=self.image_display_c_canvas.bbox('all'))

        self.image_display_d_frame.update()
        self.image_display_d_canvas.configure(scrollregion=self.image_display_d_canvas.bbox('all'))



        self.timeline_frame = tk.Frame(self.root)
        self.timeline_frame.pack(side="right", padx=10)

        self.image_info_frame = tk.Frame(self.root)
        self.image_info_frame.pack(side="right", padx=10)


        # For inputing sequences
        self.text_a = tk.StringVar()
        self.text_b = tk.StringVar()
        self.text_ocr_a = tk.StringVar()
        self.text_ocr_b = tk.StringVar()
        self.text_subtitle_a = tk.StringVar()
        self.text_subtitle_b = tk.StringVar()
        self.object_a = tk.StringVar()
        self.object_b = tk.StringVar()



        # For sequence A
        self.sequence_a_label = tk.Label(self.sequence_a_frame, text="Sequence A")
        self.sequence_a_label.grid(row=0, column=0, padx=10, pady=10)

        self.sequence_a_entry = tk.Entry(self.sequence_a_frame, textvariable=self.text_a, width=60)
        self.sequence_a_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.get_objects_a_button = tk.Button(self.sequence_a_frame, text="Get objects", command=self.get_objects_from_text)
        self.get_objects_a_button.grid(row=0, column=2, padx=10, pady=10)

        self.object_a_label = tk.Label(self.sequence_a_frame, text="Objects of A")
        self.object_a_label.grid(row=0, column=3, padx=10, pady=10)

        self.object_a_entry = tk.Entry(self.sequence_a_frame, textvariable=self.object_a, width=30)
        self.object_a_entry.grid(row=0, column=4, padx=10, pady=10)

        self.sequence_a_button_sim = tk.Button(self.sequence_a_frame, text="Search by similarity", command=lambda: self.search_sequence_a('sim'))
        self.sequence_a_button_sim.grid(row=0, column=5, padx=10, pady=10)

        self.sequence_a_button_object = tk.Button(self.sequence_a_frame, text="Search by object", command=lambda: self.search_sequence_a('object'))
        self.sequence_a_button_object.grid(row=0, column=6, padx=10, pady=10)

        self.sequence_a_button_both = tk.Button(self.sequence_a_frame, text="Search by both", command=lambda: self.search_sequence_a('both'))
        self.sequence_a_button_both.grid(row=0, column=7, padx=10, pady=10)

        # For OCR text A
        self.sequence_ocr_a_label = tk.Label(self.sequence_ocr_a_frame, text="OCR text A")
        self.sequence_ocr_a_label.grid(row=0, column=0, padx=10, pady=10)

        self.sequence_ocr_a_entry = tk.Entry(self.sequence_ocr_a_frame, textvariable=self.text_ocr_a, width=60)
        self.sequence_ocr_a_entry.grid(row=0, column=1, padx=10, pady=10)

        self.sequence_ocr_a_button = tk.Button(self.sequence_ocr_a_frame, text="Search OCR", command=lambda: self.search_ocr('a'))
        self.sequence_ocr_a_button.grid(row=0, column=2, padx=10, pady=10)

        # For subtitle text A
        self.sequence_subtitle_a_label = tk.Label(self.sequence_ocr_a_frame, text="Subtitle text A")
        self.sequence_subtitle_a_label.grid(row=0, column=3, padx=10, pady=10)

        self.sequence_subtitle_a_entry = tk.Entry(self.sequence_ocr_a_frame, textvariable=self.text_subtitle_a, width=60)
        self.sequence_subtitle_a_entry.grid(row=0, column=4, padx=10, pady=10)

        self.sequence_subtitle_a_button = tk.Button(self.sequence_ocr_a_frame, text="Search subtitle", command=lambda: self.search_subtitle('a'))
        self.sequence_subtitle_a_button.grid(row=0, column=5, padx=10, pady=10)



        # For sequence B
        self.sequence_b_label = tk.Label(self.sequence_b_frame, text="Sequence B")
        self.sequence_b_label.grid(row=0, column=0, padx=10, pady=10)

        self.sequence_b_entry = tk.Entry(self.sequence_b_frame, textvariable=self.text_b, width=60)
        self.sequence_b_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.get_objects_b_button = tk.Button(self.sequence_b_frame, text="Get objects", command=self.get_objects_from_text)
        self.get_objects_b_button.grid(row=0, column=2, padx=10, pady=10)

        self.object_b_label = tk.Label(self.sequence_b_frame, text="Objects of B")
        self.object_b_label.grid(row=0, column=3, padx=10, pady=10)

        self.object_b_entry = tk.Entry(self.sequence_b_frame, textvariable=self.object_b, width=30)
        self.object_b_entry.grid(row=0, column=4, padx=10, pady=10)

        self.sequence_b_button_sim = tk.Button(self.sequence_b_frame, text="Search by similarity", command=lambda: self.search_sequence_b('sim'))
        self.sequence_b_button_sim.grid(row=0, column=5, padx=10, pady=10)

        self.sequence_b_button_object = tk.Button(self.sequence_b_frame, text="Search by object", command=lambda: self.search_sequence_b('object'))
        self.sequence_b_button_object.grid(row=0, column=6, padx=10, pady=10)

        self.sequence_b_button_both = tk.Button(self.sequence_b_frame, text="Search by both", command=lambda: self.search_sequence_b('both'))
        self.sequence_b_button_both.grid(row=0, column=7, padx=10, pady=10)

        # For OCR text B
        self.sequence_ocr_b_label = tk.Label(self.sequence_ocr_b_frame, text="OCR text B")
        self.sequence_ocr_b_label.grid(row=0, column=0, padx=10, pady=10)

        self.sequence_ocr_b_entry = tk.Entry(self.sequence_ocr_b_frame, textvariable=self.text_ocr_b, width=60)
        self.sequence_ocr_b_entry.grid(row=0, column=1, padx=10, pady=10)

        self.sequence_ocr_b_button = tk.Button(self.sequence_ocr_b_frame, text="Search OCR", command=lambda: self.search_ocr('b'))
        self.sequence_ocr_b_button.grid(row=0, column=2, padx=10, pady=10)

        # For subtitle text B
        self.sequence_subtitle_b_label = tk.Label(self.sequence_ocr_b_frame, text="Subtitle text B")
        self.sequence_subtitle_b_label.grid(row=0, column=3, padx=10, pady=10)

        self.sequence_subtitle_b_entry = tk.Entry(self.sequence_ocr_b_frame, textvariable=self.text_subtitle_b, width=60)
        self.sequence_subtitle_b_entry.grid(row=0, column=4, padx=10, pady=10)

        self.sequence_subtitle_b_button = tk.Button(self.sequence_ocr_b_frame, text="Search subtitle", command=lambda: self.search_subtitle('b'))
        self.sequence_subtitle_b_button.grid(row=0, column=5, padx=10, pady=10)



        # self.scale = tk.Scale(self.sequence_b_frame, from_=1, to=10, orient="horizontal", length=50)
        # self.scale.grid(row=1, column=0, padx=10, pady=10)

        # # Create a button to get the slider value
        # get_value_button = tk.Button(root, text="Get Slider Value", command=self.get_slider_value)
        # get_value_button.pack()

        # Create a label to display the slider value
        # self.value_label = tk.Label(self.sequence_b_frame, text="")
        # self.value_label.grid(row=1, column=1, padx=10, pady=10)

        

        # self.image_label = tk.Label(self.image_display_frame)
        # self.image_label.pack()

        # self.image_info_label = tk.Label(self.image_info_frame, text="Image Path:")
        # self.image_info_label.pack(side="left")

        # self.image_path_label = tk.Label(self.image_info_frame, text="", wraplength=200)
        # self.image_path_label.pack(side="left")

        # self.open_image_button = tk.Button(self.image_info_frame, text="Open Image", command=self.open_image)
        # self.open_image_button.pack(side="left")


        # info frame buttons
        open_button = tk.Button(self.info_display, text="Open Video", command=self.on_open_video_click)
        open_button.pack(side = 'left')

        # Create a button to open the file dialog
        upload_button = tk.Button(self.info_display, text="Upload Image", command= self.open_file_dialog)
        upload_button.pack(side = 'left', pady=10)

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.ppm")])
        if file_path:
            # Do something with the selected file, e.g., display it in an Image widget
            print("Selected file:", file_path)

    def get_objects_from_text(self):
        print('get objects')
    
    def search_ocr(self, panel):
        topN = 100
        
        if panel == 'a':
            image_display_frame = self.image_display_a_frame
            image_display_canvas = self.image_display_a_canvas
        elif panel == 'b':
            image_display_frame = self.image_display_b_frame
            image_display_canvas = self.image_display_b_canvas

        # Xóa các ảnh của query trước đó
        for label in image_display_frame.winfo_children():
            if isinstance(label, tk.Label):
                label.destroy()

        if (panel == "a"):
            text_ocr_a = self.text_ocr_a.get()
            self.result_video_frames_a = search_text_ocr(text_ocr_a, topN)
            self.update_image_display(self.result_video_frames_a, panel)
        elif (panel == "b"):
            text_ocr_b = self.text_ocr_b.get()
            self.result_video_frames_b = search_text_ocr(text_ocr_b, topN)
            self.update_image_display(self.result_video_frames_b, panel)
        
        image_display_frame.update()
        image_display_canvas.configure(scrollregion=image_display_canvas.bbox('all'))
        print('finish search OCR')

    def search_subtitle(self, panel):
        topN = 100
        
        if panel == 'a':
            image_display_frame = self.image_display_a_frame
            image_display_canvas = self.image_display_a_canvas
        elif panel == 'b':
            image_display_frame = self.image_display_b_frame
            image_display_canvas = self.image_display_b_canvas

        # Xóa các ảnh của query trước đó
        for label in image_display_frame.winfo_children():
            if isinstance(label, tk.Label):
                label.destroy()

        if (panel == "a"):
            text_subtitle_a = self.text_subtitle_a.get()
            self.result_video_frames_a = search_text_subtitle(text_subtitle_a, topN)
            self.update_image_display(self.result_video_frames_a, panel)
        elif (panel == "b"):
            text_subtitle_b = self.text_subtitle_b.get()
            self.result_video_frames_b = search_text_subtitle(text_subtitle_b, topN)
            self.update_image_display(self.result_video_frames_b, panel)

        image_display_frame.update()
        image_display_canvas.configure(scrollregion=image_display_canvas.bbox('all'))        
        print('finish search subtitle') 

    def search_next(self, selected_video_frame):
        print('next')

        # Xóa các ảnh của query trước đó
        for label in self.image_display_d_frame.winfo_children():
            if isinstance(label, tk.Label):
                label.destroy()

        print(selected_video_frame.path, selected_video_frame.video_name, selected_video_frame.keyframe_idx)
        self.result_video_frames_d = extract_frames_neighbor(selected_video_frame, num_frames_after=30, frame_stride=15)
            
        self.update_image_display(self.result_video_frames_d, 'd')
        self.image_display_d_frame.update()
        self.image_display_d_canvas.configure(scrollregion=self.image_display_d_canvas.bbox('all'))

    def search_prev(self, selected_video_frame):
        print('prev')

        # Xóa các ảnh của query trước đó
        for label in self.image_display_d_frame.winfo_children():
            if isinstance(label, tk.Label):
                label.destroy()
        
        print(selected_video_frame.path, selected_video_frame.video_name, selected_video_frame.keyframe_idx)
        self.result_video_frames_d = extract_frames_neighbor(selected_video_frame, num_frames_after=30, frame_stride=15)
            
        self.update_image_display(self.result_video_frames_d, 'd')
        self.image_display_d_frame.update()
        self.image_display_d_canvas.configure(scrollregion=self.image_display_d_canvas.bbox('all'))

    def search_pair(self, mode):

        frame_epsilon = 500
        
        # Xóa các ảnh của query trước đó
        for label in self.image_display_c_frame.winfo_children():
            if isinstance(label, tk.Label):
                label.destroy()

        # Khởi tạo danh sách kết quả
        self.result_video_frames_c = []

        # Make pairs
        for video_frame_a in self.result_video_frames_a:
            for video_frame_b in self.result_video_frames_b:
                if (video_frame_a.video_name == video_frame_b.video_name):
                    frame_idx_a = (int)(video_frame_a.frame_idx)
                    frame_idx_b = (int)(video_frame_b.frame_idx)

                    if mode=='ab':
                        if (frame_idx_a < frame_idx_b and frame_idx_b - frame_idx_a < frame_epsilon):
                            print(video_frame_a, frame_idx_a, frame_idx_b)
                            score = (float)(video_frame_a.similarity) + (float)(video_frame_b.similarity)
                            heapq.heappush(self.result_video_frames_c, (score, {
                                'start': video_frame_a,
                                'end': video_frame_b
                            }))
                    else:
                        if (frame_idx_b < frame_idx_a and frame_idx_a - frame_idx_b < frame_epsilon):
                            print(video_frame_a, frame_idx_b, frame_idx_a)
                            score = (float)(video_frame_a.similarity) + (float)(video_frame_b.similarity)
                            heapq.heappush(self.result_video_frames_c, (score, {
                                'start': video_frame_b,
                                'end': video_frame_a
                            }))
                    
        print('Number of pairs found:', len(self.result_video_frames_c))

        self.update_image_display_pair()
        self.image_display_c_frame.update()
        self.image_display_c_canvas.configure(scrollregion=self.image_display_c_canvas.bbox('all'))

    def search_sequence_a(self, mode):
        text_a = self.text_a.get()
        object_a = text_to_list(self.object_a.get())
        self.search(text_a, object_a, 'a', mode)

    def search_sequence_b(self, mode):
        text_b = self.text_b.get()
        object_b = text_to_list(self.object_b.get())
        self.search(text_b, object_b, 'b', mode)
    
    def search(self, text, object, panel, mode):        

        if panel == 'a':
            image_display_frame = self.image_display_a_frame
            image_display_canvas = self.image_display_a_canvas
        elif panel == 'b':
            image_display_frame = self.image_display_b_frame
            image_display_canvas = self.image_display_b_canvas

        # Xóa các ảnh của query trước đó
        for label in image_display_frame.winfo_children():
            if isinstance(label, tk.Label):
                label.destroy()

        if mode == 'sim':
            view = self.dataset.sort_by_similarity(text, k=200, brain_key = BrainKey, dist_field = "similarity")
        elif mode == 'object':
            view = (
                self.dataset
                .filter_labels("object_faster_rcnn", F("label").is_in(object))
                .sort_by(F("predictions.detections").length(), reverse=True)
            )[:200]
        elif mode == 'both':
            view = (
                self.dataset
                .filter_labels("object_faster_rcnn", F("label").is_in(object))
                .sort_by_similarity(text, k=200, brain_key = BrainKey, dist_field = "similarity")
                # .sort_by(F("predictions.detections").length(), reverse=True)
            )
        
        if panel == 'a':
            self.result_video_frames_a = []
            for seq in view:
                path = seq.filepath
                video_name = seq.video
                keyframe_idx = seq.frameid
                frame_idx = get_frame_info(video_name, keyframe_idx)
                image = None
                similarity = seq.similarity
                self.result_video_frames_a.append(VideoFrame(path, video_name, keyframe_idx, frame_idx, image, similarity))
            self.update_image_display(self.result_video_frames_a, panel)
        elif panel == 'b':
            self.result_video_frames_b = []
            for seq in view:
                path = seq.filepath
                video_name = seq.video
                keyframe_idx = seq.frameid
                frame_idx = get_frame_info(video_name, keyframe_idx)
                image = None
                similarity = seq.similarity
                self.result_video_frames_b.append(VideoFrame(path, video_name, keyframe_idx, frame_idx, image, similarity))
            self.update_image_display(self.result_video_frames_b, panel)
        
        image_display_frame.update()
        image_display_canvas.configure(scrollregion=image_display_canvas.bbox('all'))
      
    def update_image_display(self, result_video_frames, panel):

        image_display_frame = None
        num_cols = 0

        if panel == 'a':
            image_display_frame = self.image_display_a_frame
            num_cols = 2
        elif panel == 'b':
            image_display_frame = self.image_display_b_frame 
            num_cols = 2       
        elif panel == 'd':
            image_display_frame = self.image_display_d_frame  
            num_cols = 3

        for i in range(len(result_video_frames)):
            video_frame = result_video_frames[i]
            path = video_frame.path
            video_name = video_frame.video_name
            frame_idx = video_frame.frame_idx
            # print(path, video_name, frame_idx)

            if path != "":
                try: 
                    image = Image.open(path).resize((160, 90), Image.LANCZOS)
                except:
                    continue
                photo = ImageTk.PhotoImage(image)
            else:
                photo = extract_photo(video_name, frame_idx)

            # Create a label for the image
            label = tk.Label(image_display_frame, image=photo)
            label.configure(image=photo)
            label.image = photo
            label.grid(row=i//num_cols, column=i%num_cols)

            # Create a label for the video name and frame index
            filename_label = tk.Label(image_display_frame, text=f"{video_name}, {frame_idx}", anchor='sw', bg='white')
            filename_label.grid(row=i // num_cols, column=i % num_cols, sticky='sw')

            # Bind a click event to the image label
            label.bind("<Button-1>", lambda e, video_frame=result_video_frames[i]: self.on_image_click(panel=panel, video_frame=video_frame))

        print(f"Found {len(result_video_frames)} images.")

    def update_image_display_pair(self):
        
        for i in range(len(self.result_video_frames_c)):

            video_frame_start = self.result_video_frames_c[i][1]['start']
            video_frame_end = self.result_video_frames_c[i][1]['end']

            path_start = video_frame_start.path
            path_end = video_frame_end.path
            video_name = video_frame_start.video_name
            frame_idx_start = video_frame_start.frame_idx
            frame_idx_end =video_frame_end.frame_idx
            
            try: 
                image_start = Image.open(path_start).resize((160, 90), Image.LANCZOS)
            except:
                continue
            try: 
                image_end = Image.open(path_end).resize((160, 90), Image.LANCZOS)
            except:
                continue
            photo_start = ImageTk.PhotoImage(image_start)
            photo_end = ImageTk.PhotoImage(image_end)

            label_start = tk.Label(self.image_display_c_frame, image=photo_start)
            label_start.configure(image=photo_start)
            label_start.image = photo_start
            label_start.grid(row=i, column=0)
            filename_label_start = tk.Label(self.image_display_c_frame, text=f"{video_name}, {frame_idx_start}", anchor='sw', bg='white')
            filename_label_start.grid(row=i, column=0, sticky='sw')
            label_start.bind("<Button-1>", lambda e, _video_frame_start=video_frame_start, _video_frame_end=video_frame_end: self.on_pair_click(panel="c", video_frame_start=_video_frame_start, video_frame_end=_video_frame_end))

            label_end = tk.Label(self.image_display_c_frame, image=photo_end)
            label_end.configure(image=photo_end)
            label_end.image = photo_end
            label_end.grid(row=i, column=1)
            filename_label_start = tk.Label(self.image_display_c_frame, text=f"{video_name}, {frame_idx_end}", anchor='sw', bg='white')
            filename_label_start.grid(row=i, column=1, sticky='sw')
            label_start.bind("<Button-1>", lambda e, _video_frame_start=video_frame_start, _video_frame_end=video_frame_end: self.on_pair_click(panel="c", video_frame_start=_video_frame_start, video_frame_end=_video_frame_end))

    def on_image_click(self, panel = "", video_frame=None):
        path = video_frame.path
        video_name = video_frame.video_name
        frame_idx = video_frame.frame_idx

        print(f"Image clicked: {path}, {video_name}, {frame_idx}, panel: {panel}")
        self.selected_video_path = VideosFolder + '\\' + video_name + '.mp4'

        if panel == "a":
            self.selected_video_frame_a = video_frame
        elif panel == "b":
            self.selected_video_frame_b = video_frame
        elif panel == "d":
            if not os.path.exists(ResultsCSV):                
                os.makedirs(ResultsCSV)
            submission_filepath = ResultsCSV + str(self.text_a.get()[:20]) + '.csv'
            if os.path.exists(submission_filepath):
                with open(submission_filepath, mode='a', newline='') as file:
                    writer = csv.writer(file, delimiter=',')
                    writer.writerow([video_name, frame_idx])  
                    file.close()
            else:
                with open(submission_filepath, mode='w', newline='') as file:
                    writer = csv.writer(file, delimiter=',')
                    writer.writerow([video_name, frame_idx]) 
                    file.close()             
        
        # self.image_path_label.config(text = path)

    def on_pair_click(self, panel = "", video_frame_start=None, video_frame_end=None):
        if panel != "c":
            return None
        
        video_name = video_frame_start.video_name
        self.selected_video_path = VideosFolder + '\\' + video_name + '.mp4'
        self.result_video_frames_d = extract_frames_between(video_frame_start, video_frame_end)

        #Hiển thị lên panel
        self.update_image_display(self.result_video_frames_d, panel="d")
        self.image_display_d_frame.update()
        self.image_display_d_canvas.configure(scrollregion=self.image_display_d_canvas.bbox('all'))

    def on_open_video_click(self):

        file_path = self.selected_video_path

        # Use the "start" command on Windows to open the file with the default associated program.
        subprocess.Popen(['start', '', file_path], shell=True)

    def display_image(self):
        image_path = self.current_image_paths[self.current_image_index]
        image = Image.open(image_path)
        image = image.resize((400, 400), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image=image)
        self.image_label.config(image=photo)
        self.image_label.image = photo
        # self.image_path_label.config(text="Image Path: " + image_path)

    def open_image(self):
        image_path = self.current_image_paths[self.current_image_index]
        image = Image.open(image_path)
        image.show()

if __name__ == "__main__":

    dataset = fo.load_dataset(DatasetName)
    root = tk.Tk()
    app = ImageApp(root, dataset)
    root.mainloop()
