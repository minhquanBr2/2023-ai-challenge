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

import heapq
from mapping_keyframe import get_frame_info, parse_direc
from extract_frame import extract_frames
from GlobalLink import KeyframeFolder

# to do
# image_folder = 

selected_1_img = ""
selected_2_img = ""

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
        self.framewidth_unit = int(self.screenwidth / 9 * 0.95)

        # FOR INPUT
        # ở đây ta có 2 frame ở vị trí top, mỗi frame ứng với 1 dòng label + 1 ô nhập text + 1 nút search
        self.sequence_a_frame = tk.Frame(self.root)
        self.sequence_a_frame.pack(side="top")

        self.sequence_b_frame = tk.Frame(self.root)
        self.sequence_b_frame.pack(side="top")



        # image_display: là cái frame được dùng như grid để bố trí các thành phần trên cửa sổ
        self.image_display = tk.Frame(self.root)
        self.image_display.pack(side="left", padx=10)

        self.image_display_a = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500, background="red")
        self.image_display_a.grid(row=0, column=0)

        self.image_display_b = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500, background="green")
        self.image_display_b.grid(row=0, column=1)
        
        self.image_display_c = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500, background="red")
        self.image_display_c.grid(row=0, column=2)

        self.image_display_d = tk.Frame(self.image_display, width=3*self.framewidth_unit, height=500, background="green")
        self.image_display_d.grid(row=0, column=3)


        # 3 search buttons at the bottom
        self.search_a_next_button = tk.Button(self.image_display, text="Search next", command=self.search_a_next)
        self.search_a_next_button.grid(row=1, column=0)
    
        self.search_b_prev_button = tk.Button(self.image_display, text="Search prev", command=self.search_b_prev)
        self.search_b_prev_button.grid(row=1, column=1)

        self.search_pair_button = tk.Button(self.image_display, text="Search pair", command=self.search_pair)
        self.search_pair_button.grid(row=2, column=0, columnspan=2)

        


        # FOR IMAGE DISPLAYING
        self.image_display_a_canvas = tk.Canvas(self.image_display_a, width=2*self.framewidth_unit, height=500, background="blue")
        self.image_display_a_canvas.pack(side="left", fill="both", expand=True)

        self.image_display_b_canvas = tk.Canvas(self.image_display_b, width=2*self.framewidth_unit, height=500, background="cyan")
        self.image_display_b_canvas.pack(side="left", fill="both", expand=True)

        self.image_display_c_canvas = tk.Canvas(self.image_display_c, width=2*self.framewidth_unit, height=500, background="magenta")
        self.image_display_c_canvas.pack(side="left", fill="both", expand=True)

        self.image_display_d_canvas = tk.Canvas(self.image_display_d, width=3*self.framewidth_unit, height=500, background="blue")
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
        self.image_display_a_frame = tk.Frame(self.image_display_a_canvas, background='green')
        self.image_display_a_canvas.create_window((0, 0), window=self.image_display_a_frame, anchor="nw")
        self.image_display_b_frame = tk.Frame(self.image_display_b_canvas, background='green')
        self.image_display_b_canvas.create_window((0, 0), window=self.image_display_b_frame, anchor="nw")
        self.image_display_c_frame = tk.Frame(self.image_display_c_canvas, background='yellow')
        self.image_display_c_canvas.create_window((0, 0), window=self.image_display_c_frame, anchor="nw")
        self.image_display_d_frame = tk.Frame(self.image_display_d_canvas, background='red')
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

        self.text_a = tk.StringVar()
        self.text_b = tk.StringVar()

        self.sequence_a_label = tk.Label(self.sequence_a_frame, text="Sequence A")
        self.sequence_a_label.grid(row=0, column=0, padx=10, pady=10)

        self.sequence_a_entry = tk.Entry(self.sequence_a_frame, textvariable=self.text_a)
        self.sequence_a_entry.grid(row=0, column=1, padx=10, pady=10)

        self.sequence_a_button = tk.Button(self.sequence_a_frame, text="Search", command=self.search_sequence_a)
        self.sequence_a_button.grid(row=0, column=2, padx=10, pady=10)

        self.sequence_b_label = tk.Label(self.sequence_b_frame, text="Sequence B")
        self.sequence_b_label.grid(row=0, column=0, padx=10, pady=10)

        self.sequence_b_entry = tk.Entry(self.sequence_b_frame, textvariable=self.text_b)
        self.sequence_b_entry.grid(row=0, column=1, padx=10, pady=10)

        self.sequence_b_button = tk.Button(self.sequence_b_frame, text="Search", command=self.search_sequence_b)
        self.sequence_b_button.grid(row=0, column=2, padx=10, pady=10)

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


    def search_a_next(self):
        print('next')
        if selected_1_img == "":
            print("a: No image select")
            return False
        
        parse_res = parse_direc(selected_1_img)
        video_name = parse_res['video_name']
        key_frame = parse_res['kframe']

        #Lấy frameidx của hình được select
        frame_idx = get_frame_info(video_name=video_name, keyframe_name=key_frame)['frame_idx']
        images = []
        print("Frame index: ", frame_idx)

        #Lấy các frameidx từ video ra
        images = extract_frames(video_name=video_name, frame_idx=frame_idx, num_frames_after= 30, frame_stride=15)
        #Hiển thị lên panel
        self.update_image_display_from_ImageTK(images, panel="c")
        self.image_display_c_frame.update()
        self.image_display_c_canvas.configure(scrollregion=self.image_display_c_canvas.bbox('all'))


    def search_b_prev(self):
        print('prev')
        if selected_2_img == "":
            print("b: No image select")
            return False
        
        parse_res = parse_direc(selected_2_img)
        video_name = parse_res['video_name']
        key_frame = parse_res['kframe']

        #Lấy frameidx của hình được select
        frame_idx = get_frame_info(video_name=video_name, keyframe_name=key_frame)['frame_idx']
        images = []
        print("Frame index: ", frame_idx)
       
        images = extract_frames(video_name=video_name, frame_idx=frame_idx, num_frames_before= 30, frame_stride=15)

        #Hiển thị lên panel
        self.update_image_display_from_ImageTK(images, panel="c")
        self.image_display_c_frame.update()
        self.image_display_c_canvas.configure(scrollregion=self.image_display_c_canvas.bbox('all'))
        
    def search_pair(self, frame_epsilon=10):
        
        # Xóa các ảnh của query trước đó
        for label in self.image_display_c_frame.winfo_children():
            if isinstance(label, tk.Label):
                label.destroy()

        # Khởi tạo danh sách kết quả
        self.image_labels_pair = []
        results = []
        print(len(self.view_a))
        print(len(self.view_b))

        # Make pairs
        for seqA in self.view_a:
            for seqB in self.view_b:
                if (seqA.video == seqB.video):
                    frameA = (int)(seqA.frameid)
                    frameB = (int)(seqB.frameid)
                    print(seqA.video, frameA, frameB)
                    if (frameA < frameB and frameB - frameA < frame_epsilon):
                        score = (float)(seqA.similarity) + (float)(seqB.similarity)
                        heapq.heappush(results, (score, {
                            'filepathA': seqA.filepath,
                            'filepathB': seqB.filepath,
                            'video': seqA.video,
                            'seqA': seqA.frameid,
                            'seqB': seqB.frameid,
                        }))
                    print(len(results))

        for i in range(len(results)):

            pathA = results[i][1]['filepathA']
            pathB = results[i][1]['filepathB']
            print(pathA, pathB)

            imageA = Image.open(pathA).resize((160, 90), Image.LANCZOS)
            imageB = Image.open(pathB).resize((160, 90), Image.LANCZOS)
            photoA = ImageTk.PhotoImage(imageA)
            photoB = ImageTk.PhotoImage(imageB)

            labelA = tk.Label(self.image_display_c_frame, image=photoA)
            labelA.configure(image=photoA)
            labelA.image = photoA
            labelA.grid(row=i, column=0)
            labelA.bind("<Button-1>", lambda e, path=pathA: self.on_image_click(path, "a"))   # chua hieu

            labelB = tk.Label(self.image_display_c_frame, image=photoB)
            labelB.configure(image=photoB)
            labelB.image = photoB
            labelB.grid(row=i, column=1)
            labelB.bind("<Button-1>", lambda e, path=pathB: self.on_image_click(path, "b"))   # chua hieu

            self.image_labels_pair.append([labelA, labelB])
            print("Number of pairs:", len(self.image_labels_pair))

        self.image_display_c_frame.update()
        self.image_display_c_canvas.configure(scrollregion=self.image_display_c_canvas.bbox('all'))

    def search_sequence_a(self):
        text_a = self.text_a.get()
        self.search(text_a, 'a')

    def search_sequence_b(self):
        text_b = self.text_b.get()
        self.search(text_b, 'b')

    def get_slider_value(self):
        value = self.scale.get()
        self.value_label.config(text=f"Slider Value: {value}")

        return value
    
    def search(self, text, panel):

        if panel == 'a':
            image_display_frame = self.image_display_a_frame
            image_display_canvas = self.image_display_a_canvas
        elif panel == 'b':
            image_display_frame = self.image_display_b_frame
            image_display_canvas = self.image_display_b_canvas

        view = self.dataset.sort_by_similarity(text, k=100, brain_key = "img_sim_32_qdrant", dist_field = "similarity")
        images_paths = []

        for seq in view:
            curVideo, curFrame = seq.video, seq.frameid
            images_paths.append(seq.filepath)

        self.update_image_display_from_path(images_paths, panel)
        image_display_frame.update()
        image_display_canvas.configure(scrollregion=image_display_canvas.bbox('all'))

        if panel == 'a':
            self.view_a = view
        elif panel == 'b':
            self.view_b = view


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
            path = image_paths[i]
            print(path)
            image = Image.open(path)
            image = image.resize((160, 90), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(image_display_frame, image=photo)
            label.configure(image=photo)
            label.image = photo
            label.grid(row=i//2, column=i%2)
            label.bind("<Button-1>", lambda e, path=path: self.on_image_click(path, panel))
            image_labels.append(label)

    def update_image_display_from_ImageTK(self, images, panel):

        image_labels = None
        image_display_frame = None
        if panel == 'c':
            self.image_labels_c = []
            image_labels = self.image_labels_c
            image_display_frame = self.image_display_c_frame
        elif panel == 'd':
            self.image_labels_d = []
            image_labels = self.image_labels_d
            image_display_frame = self.image_display_d_frame
        
        else:
            return None

        for i in range(len(images)):
            # image = images[i]
            # image = image.resize((160, 90), Image.LANCZOS)
            # photo = ImageTk.PhotoImage(image)
            photo = images[i]
            label = tk.Label(image_display_frame, image=photo)
            label.configure(image=photo)
            label.image = photo
            label.grid(row=i//2, column=i%2)
            # label.bind("<Button-1>", lambda e, path=path: self.on_image_click(path))
            image_labels.append(label)


    def on_image_click(self, image_path, panel = ""):
        print(f"Image clicked: {image_path}, panel: {panel}")
        global selected_1_img
        global selected_2_img

        if panel == "a":
            selected_1_img = image_path
        elif panel == "b":
            selected_2_img = image_path
        self.image_path_label.config(text = image_path)

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
    # dataset = fo.Dataset.from_images_dir(KeyframeFolder, name="aic2023-full", tags=None, recursive=True)
    # dataset.persistent = True
    dataset = fo.load_dataset('aic2023-full')

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
    #     collection_name = "aic2023-full"
    # )
    # dataset.save()

    root = tk.Tk()
    app = ImageApp(root, dataset)
    
    # session = fo.launch_app(dataset, desktop=True)
    

    root.mainloop()
