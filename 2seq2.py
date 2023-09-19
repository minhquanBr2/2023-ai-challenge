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
from mapping_keyframe import get_frame_info, parse_direc
from extract_frame import extract_frames, extract_frames_between
from GlobalLink import KeyframeFolder, ResultsCSV, VideosFolder, BrainKey, DatasetName

import subprocess

# to do
# image_folder = 

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
        self.image_labels_a = []
        self.image_labels_b = []
        self.image_labels_pair = []
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
        self.sequence_a_frame.pack(side="top")

        self.sequence_b_frame = tk.Frame(self.root)
        self.sequence_b_frame.pack(side="top")

        # info_display: frame dùng để hiển thị thông tin của frame đã chọn
        self.info_display = tk.Frame(self.root)
        self.info_display.pack(side = "top")

        # SELECTED IMAGE: các biến lưu các ảnh được chọn
        self.selected_img_a = ""
        self.selected_img_b = ""

        # image_display: là cái frame được dùng như grid để bố trí các thành phần trên cửa sổ
        self.image_display = tk.Frame(self.root)
        self.image_display.pack(side="left", padx=10)

        self.image_display_a = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500)
        self.image_display_a.grid(row=0, column=0, columnspan=2)

        self.image_display_b = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500)
        self.image_display_b.grid(row=0, column=2, columnspan=2)
        
        self.image_display_c = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500)
        self.image_display_c.grid(row=0, column=4, columnspan=2)

        self.image_display_d = tk.Frame(self.image_display, width=3*self.framewidth_unit, height=500)
        self.image_display_d.grid(row=0, column=6, columnspan=2)


        # 6 search buttons at the bottom
        self.search_a_prev_button = tk.Button(self.image_display, text="Search prev of A", command=lambda: self.search_prev(self.selected_img_a))
        self.search_a_prev_button.grid(row=1, column=0, sticky=tk.E)

        self.search_a_next_button = tk.Button(self.image_display, text="Search next of A", command=lambda: self.search_next(self.selected_img_a))
        self.search_a_next_button.grid(row=1, column=1, sticky=tk.W)
    
        self.search_b_prev_button = tk.Button(self.image_display, text="Search prev of B", command=lambda: self.search_prev(self.selected_img_b))
        self.search_b_prev_button.grid(row=1, column=2, sticky=tk.E)
    
        self.search_b_next_button = tk.Button(self.image_display, text="Search next of B", command=lambda: self.search_next(self.selected_img_b))
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

        # # Configure the Canvas to use the Scrollbar
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



        self.scale = tk.Scale(self.sequence_b_frame, from_=1, to=10, orient="horizontal", length=50)
        self.scale.grid(row=1, column=0, padx=10, pady=10)

        # # Create a button to get the slider value
        # get_value_button = tk.Button(root, text="Get Slider Value", command=self.get_slider_value)
        # get_value_button.pack()

        # Create a label to display the slider value
        self.value_label = tk.Label(self.sequence_b_frame, text="")
        self.value_label.grid(row=1, column=1, padx=10, pady=10)

        

        # self.image_label = tk.Label(self.image_display_frame)
        # self.image_label.pack()

        self.image_info_label = tk.Label(self.image_info_frame, text="Image Path:")
        self.image_info_label.pack(side="left")

        self.image_path_label = tk.Label(self.image_info_frame, text="", wraplength=200)
        self.image_path_label.pack(side="left")

        # self.open_image_button = tk.Button(self.image_info_frame, text="Open Image", command=self.open_image)
        # self.open_image_button.pack(side="left")


        # info frame buttons
        open_button = tk.Button(self.info_display, text="Open Video", command=self.on_open_video_click)
        open_button.pack()

    def get_objects_from_text(self):
        print('get objects')

    def search_next(self, selected_img):
        print('next')
        if selected_img == "":
            print("No image selected.")
            return False
        
        parse_res = parse_direc(selected_img)
        video_name = parse_res['video_name']
        key_frame = parse_res['kframe']

        #Lấy frameidx của hình được select
        frame_idx = get_frame_info(video_name=video_name, keyframe_name=key_frame)['frame_idx']
        images = []
        print("Frame index: ", frame_idx)

        #Lấy các frameidx từ video ra
        video_name, frame_indices, images = extract_frames(video_name=video_name, frame_idx=frame_idx, num_frames_after= 30, frame_stride=15)
        #Hiển thị lên panel
        self.update_image_display_from_ImageTK(images, panel="d", video_name=video_name, frame_indices=frame_indices)
        self.image_display_d_frame.update()
        self.image_display_d_canvas.configure(scrollregion=self.image_display_d_canvas.bbox('all'))


    def search_prev(self, selected_img):
        print('prev')
        if selected_img == "":
            print("No image selected.")
            return False
        
        parse_res = parse_direc(selected_img)
        video_name = parse_res['video_name']
        key_frame = parse_res['kframe']

        #Lấy frameidx của hình được select
        frame_idx = get_frame_info(video_name=video_name, keyframe_name=key_frame)['frame_idx']
        images = []
        print("Frame index: ", frame_idx)
       
        video_name, frame_indices, images = extract_frames(video_name=video_name, frame_idx=frame_idx, num_frames_before= 30, frame_stride=15)

        #Hiển thị lên panel
        self.update_image_display_from_ImageTK(images, panel="d", video_name=video_name, frame_indices=frame_indices)
        self.image_display_d_frame.update()
        self.image_display_d_canvas.configure(scrollregion=self.image_display_d_canvas.bbox('all'))
        
    def search_pair(self, mode):

        frame_epsilon = 10
        
        # Xóa các ảnh của query trước đó
        for label in self.image_display_c_frame.winfo_children():
            if isinstance(label, tk.Label):
                label.destroy()

        # Khởi tạo danh sách kết quả
        self.image_labels_pair = []
        results = []

        # Make pairs
        for seqA in self.view_a:
            for seqB in self.view_b:
                if (seqA.video == seqB.video):
                    frameA = (int)(seqA.frameid)
                    frameB = (int)(seqB.frameid)

                    if mode=='ab':
                        if (frameA < frameB and frameB - frameA < frame_epsilon):
                            print(seqA.video, frameA, frameB)
                            score = (float)(seqA.similarity) + (float)(seqB.similarity)
                            heapq.heappush(results, (score, {
                                'filepath_start': seqA.filepath,
                                'filepath_end': seqB.filepath,
                                'video': seqA.video,
                                'frame_start': seqA.frameid,
                                'frame_end': seqB.frameid,
                            }))
                    else:
                        if (frameB < frameA and frameA - frameB < frame_epsilon):
                            print(seqA.video, frameB, frameA)
                            score = (float)(seqA.similarity) + (float)(seqB.similarity)
                            heapq.heappush(results, (score, {
                                'filepath_start': seqB.filepath,
                                'filepath_end': seqA.filepath,
                                'video': seqA.video,
                                'frame_start': seqB.frameid,
                                'frame_end': seqA.frameid,
                            }))
                    
        print('Number of pairs found:', len(results))

        for i in range(len(results)):

            path_start = results[i][1]['filepath_start']
            path_end = results[i][1]['filepath_end']
            video_name = results[i][1]['video']
            frame_index_start = results[i][1]['frame_start']
            frame_index_end = results[i][1]['frame_end']

            image_start = Image.open(path_start).resize((160, 90), Image.LANCZOS)
            image_end = Image.open(path_end).resize((160, 90), Image.LANCZOS)
            photo_start = ImageTk.PhotoImage(image_start)
            photo_end = ImageTk.PhotoImage(image_end)

            label_start = tk.Label(self.image_display_c_frame, image=photo_start)
            label_start.configure(image=photo_start)
            label_start.image = photo_start
            label_start.grid(row=i, column=0)
            filename_label_start = tk.Label(self.image_display_c_frame, text=f"{video_name}, {frame_index_end}", anchor='sw', bg='white')
            filename_label_start.grid(row=i, column=0, sticky='sw')
            label_start.bind("<Button-1>", lambda e, _path_start=path_start, _path_end=path_end: self.on_pair_click(panel="c", image_path_start=_path_start, image_path_end=_path_end))   # chua hieu

            label_end = tk.Label(self.image_display_c_frame, image=photo_end)
            label_end.configure(image=photo_end)
            label_end.image = photo_end
            label_end.grid(row=i, column=1)
            filename_label_start = tk.Label(self.image_display_c_frame, text=f"{video_name}, {frame_index_start}", anchor='sw', bg='white')
            filename_label_start.grid(row=i, column=1, sticky='sw')
            label_end.bind("<Button-1>", lambda e, _path_start=path_start, _path_end=path_end: self.on_pair_click(panel="c", image_path_start=_path_start, image_path_end=_path_end))

            self.image_labels_pair.append([label_start, label_end])

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

    def get_slider_value(self):
        value = self.scale.get()
        self.value_label.config(text=f"Slider Value: {value}")
        return value
    
    def search(self, text, object, panel, mode):

        if panel == 'a':
            image_display_frame = self.image_display_a_frame
            image_display_canvas = self.image_display_a_canvas
        elif panel == 'b':
            image_display_frame = self.image_display_b_frame
            image_display_canvas = self.image_display_b_canvas

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
                .sort_by_similarity(text, k=200, brain_key = BrainKey, dist_field = "similarity")
                .filter_labels("object_faster_rcnn", F("label").is_in(object))
                .sort_by(F("predictions.detections").length(), reverse=True)
            )[:200]
        
        images_paths = []

        for seq in view:
            images_paths.append((seq.filepath, seq.video, seq.frameid))

        self.update_image_display_from_path(images_paths, panel)
        image_display_frame.update()
        image_display_canvas.configure(scrollregion=image_display_canvas.bbox('all'))

        if panel == 'a':
            self.view_a = view
        elif panel == 'b':
            self.view_b = view

    # def on_label_click(self, event):
    #     self.config(borderwidth=2, relief="solid", highlightbackground="yellow")

    def update_image_display_from_path(self, image_paths, panel):

        image_labels = None
        image_display_frame = None
        if panel == 'a':
            self.image_labels_a = []
            image_labels = self.image_labels_a
            image_display_frame = self.image_display_a_frame
        elif panel == 'b':
            self.image_labels_b = []
            image_labels = self.image_labels_b
            image_display_frame = self.image_display_b_frame        
        else:
            return None

        for i in range(len(image_paths)):
            path, video_name, keyframe_index = image_paths[i]

            image = Image.open(path)
            image = image.resize((160, 90), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            # Create a label for the image
            label = tk.Label(image_display_frame, image=photo)
            label.configure(image=photo)
            label.image = photo
            label.grid(row=i//2, column=i%2)

            # Create a label for the video name and frame index
            filename_label = tk.Label(image_display_frame, text=f"{video_name}, {keyframe_index}, {get_frame_info(video_name, keyframe_index)}", anchor='sw', bg='white')
            filename_label.grid(row=i // 2, column=i % 2, sticky='sw')

            # Bind a click event to the image label

            label.bind("<Button-1>", lambda e, path=path, video_name=video_name, frame_index=keyframe_index: self.on_image_click(panel=panel, image_path=path, video_name=video_name, frame_index=frame_index))

            # Add label to list
            image_labels.append(label)

        print(f"Found {len(image_paths)} images.")

    def update_image_display_from_ImageTK(self, images, panel, video_name, frame_indices):

        image_labels = None
        image_display_frame = None
        if panel == 'd':
            self.image_labels_d = []
            image_labels = self.image_labels_d
            image_display_frame = self.image_display_d_frame        
        else:
            return None
        
        print('Frame indices:', frame_indices)

        for i in range(len(images)):
            # image = images[i]
            # image = image.resize((160, 90), Image.LANCZOS)
            # photo = ImageTk.PhotoImage(image)
            photo = images[i]
            frame_index = frame_indices[i]

            # Create a label for the image
            label = tk.Label(image_display_frame, image=photo)
            label.configure(image=photo)
            label.image = photo
            label.grid(row=i//3, column=i%3)

            # Create a label for the video name and frame index
            filename_label = tk.Label(image_display_frame, text=f"{video_name}, {frame_index}", anchor='sw', bg='white')
            filename_label.grid(row=i//3, column=i%3, sticky='sw')

            # Bind a click event to the image label
            label.bind("<Button-1>", lambda e, photo=photo, frame_index=frame_index: self.on_image_click(panel='d', video_name=video_name, frame_index=frame_index))
            image_labels.append(label)
            
        self.image_display_d_frame.update()
        self.image_display_d_canvas.configure(scrollregion=self.image_display_d_canvas.bbox('all'))

    def on_pair_click(self, panel = "", image_path_start=None, image_path_end = None):
        if panel != "c":
            return None
        
        video_name = parse_direc(image_path_start)['video_name']
        kframe_start = parse_direc(image_path_start)['kframe']
        frame_idx_start = get_frame_info(video_name=video_name, keyframe_name=kframe_start)['frame_idx']
        kframe_end = parse_direc(image_path_end)['kframe']
        frame_idx_end = get_frame_info(video_name=video_name, keyframe_name=kframe_end)['frame_idx']
        video_name, frame_indices, photo_images = extract_frames_between(video_name=video_name, start_frame_idx=frame_idx_start, end_frame_idx=frame_idx_end)

        #Hiển thị lên panel
        self.update_image_display_from_ImageTK(photo_images, panel="d", video_name=video_name, frame_indices=frame_indices)
        self.image_display_d_frame.update()
        self.image_display_d_canvas.configure(scrollregion=self.image_display_d_canvas.bbox('all'))




    def on_image_click(self, panel = "", image_path=None, video_name=None, frame_index=None):
        print(f"Image clicked: {image_path}, {video_name}, {frame_index}, panel: {panel}")
        self.selected_video_path = VideosFolder + '\\' + video_name + '.mp4'

        if panel == "a":
            self.selected_img_a = image_path
        elif panel == "b":
            self.selected_img_b = image_path
        elif panel == "d":
            if not os.path.exists(ResultsCSV):                
                os.makedirs(ResultsCSV)
            submission_filepath = ResultsCSV + str(self.text_a.get()[:20]) + '.csv'
            if os.path.exists(submission_filepath):
                with open(submission_filepath, mode='a', newline='') as file:
                    writer = csv.writer(file, delimiter=',')
                    writer.writerow([video_name, frame_index])  
                    file.close()
            else:
                with open(submission_filepath, mode='w', newline='') as file:
                    writer = csv.writer(file, delimiter=',')
                    writer.writerow([video_name, frame_index]) 
                    file.close()             
        self.image_path_label.config(text = image_path)

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
        self.image_path_label.config(text="Image Path: " + image_path)

    

    def open_image(self):
        image_path = self.current_image_paths[self.current_image_index]
        image = Image.open(image_path)
        image.show()

if __name__ == "__main__":
    

    # set up data
    # dataset = fo.Dataset.from_images_dir(KeyframeFolder, name="aic2023-L01-L20", tags=None, recursive=True)
    # dataset.persistent = True

    dataset = fo.load_dataset(DatasetName)

    # for sample in dataset:
    #     _, sample['video'], sample['frameid'] = sample['filepath'][:-4].rsplit('\\', 2)
    #     sample.save()
    # for sample in dataset:
    #     _, sample['video'], sample['frameid'] = sample['filepath'][:-4].rsplit('\\', 2)
    #     sample.save()

    # all_keyframe = glob(KeyframeFolder + '\\*\\*.jpg')
    # video_keyframe_dict = {}
    # all_video = glob(KeyframeFolder + '\\*')
    # all_video = [v.rsplit('\\', 1)[-1] for v in all_video]
    # print(all_video)

    # for kf in all_keyframe:
    #     _, vid, kf = kf[:-4].rsplit('\\',2)
    #     if vid not in video_keyframe_dict.keys():
    #         video_keyframe_dict[vid] = [kf]
    #     else:
    #         video_keyframe_dict[vid].append(kf)

    # for k,v in video_keyframe_dict.items():
    #     video_keyframe_dict[k] = sorted(v)

    # embedding_dict = {}
    # for v in all_video:
    #     clip_path = f'E:\\AIChallenge\\clip-features-vit-b32\\{v}.npy'
    #     a = np.load(clip_path)
    #     embedding_dict[v] = {}
    #     for i,k in enumerate(video_keyframe_dict[v]):
    #         embedding_dict[v][k] = a[i]
    #         # print(i, k, a[i])

    # clip_embeddings = []
    # for sample in dataset:
    #     clip_embedding = embedding_dict[sample['video']][sample['frameid']]
    #     clip_embeddings.append(clip_embedding)

    # # fob.compute_similarity(
    # #     dataset,
    # #     model="clip-vit-base32-torch",      # store model's name for future use
    # #     embeddings=clip_embeddings,          # precomputed image embeddings
    # #     brain_key="img_sim_32_qdrant",
    # # )


    # fob.similarity.Similarity.delete_run(dataset, "img_sim_32_qdrant")
    # # if fob.similarity.Similarity.has_cached_run_results(dataset, "img_sim_32_qdrant"):
    # #     fob.similarity.Similarity.delete_run(dataset, "img_sim_32_qdrant")

    # qdrant_index = fob.compute_similarity(
    #     dataset, 
    #     model = "clip-vit-base32-torch",     
    #     embeddings=clip_embeddings,          # precomputed image embeddings  
    #     brain_key = "img_sim_32_qdrant", 
    #     backend="qdrant",
    #     metric="cosine",
    #     collection_name = "aic2023-L01-L20"
    # )
    # dataset.save()

    root = tk.Tk()
    app = ImageApp(root, dataset)
    
    # session = fo.launch_app(dataset, desktop=True)
    

    root.mainloop()
