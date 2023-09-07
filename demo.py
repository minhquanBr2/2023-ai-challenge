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

# to do
# image_folder = 

class ImageApp:


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
        self.framewidth_unit = self.screenwidth//9


        # image_display: là cái frame được dùng như grid để bố trí các thành phần trên cửa sổ
        self.image_display = tk.Frame(self.root)
        self.image_display.pack(side="left", padx=10)

        self.image_display_a = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500, background="red")
        self.image_display_a.grid(row=0, column=0)

        self.image_display_b = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500, background="green")
        self.image_display_b.grid(row=0, column=1)
        
        self.image_display_c = tk.Frame(self.image_display, width=2*self.framewidth_unit, height=500, background="yellow")
        self.image_display_c.grid(row=0, column=2)

        self.image_display_d = tk.Frame(self.image_display, width=3*self.framewidth_unit, height=500, background="violet")
        self.image_display_d.grid(row=0, column=3)



        # FOR IMAGE DISPLAYING
        self.image_display_a_canvas = tk.Canvas(self.image_display_a, background="blue")
        self.image_display_a_canvas.grid(row=0, column=0)

        self.image_display_b_canvas = tk.Canvas(self.image_display_b, background="cyan")
        self.image_display_b_canvas.grid(row=0, column=0)

        self.image_display_c_canvas = tk.Canvas(self.image_display_c, background="magenta")
        self.image_display_c_canvas.grid(row=0, column=0)
        
        self.image_display_d_canvas = tk.Canvas(self.image_display_d, background="yellow")
        self.image_display_d_canvas.grid(row=0, column=0)



        # Create a Scrollbar for the Canvas
        self.scrollbar_a = tk.Scrollbar(self.image_display_a, orient="vertical", command=self.image_display_a_canvas.yview)
        self.scrollbar_a.grid(row=0, column=1, sticky='ns')
        self.image_display_a_canvas.configure(yscrollcommand=self.scrollbar_a.set)
        self.image_display_a_frame = tk.Frame(self.image_display_a_canvas)
        self.image_display_a_frame.pack(expand=True)
        self.image_display_a_canvas.create_window((0,0), window=self.image_display_a_frame, anchor=tk.NW)
        self.image_display_a_canvas.configure(scrollregion=self.image_display_a_canvas.bbox('all'))

        self.scrollbar_b = tk.Scrollbar(self.image_display_b, orient="vertical", command=self.image_display_b_canvas.yview)
        self.scrollbar_b.grid(row=0, column=1, sticky='ns')
        self.image_display_b_canvas.configure(yscrollcommand=self.scrollbar_b.set)
        self.image_display_b_frame = tk.Frame(self.image_display_b_canvas)
        self.image_display_b_frame.pack(fill="both", expand=True)
        self.image_display_b_canvas.create_window((0,0), window=self.image_display_b_frame, anchor=tk.NW)
        self.image_display_b_canvas.configure(scrollregion=self.image_display_b_canvas.bbox('all'))

        self.scrollbar_c = tk.Scrollbar(self.image_display_c, orient="vertical", command=self.image_display_c_canvas.yview)
        self.scrollbar_c.grid(row=0, column=1, sticky='ns')
        self.image_display_c_canvas.configure(yscrollcommand=self.scrollbar_c.set)
        self.image_display_c_frame = tk.Frame(self.image_display_c_canvas)
        self.image_display_c_frame.pack(fill="both", expand=True)
        self.image_display_c_canvas.create_window((0,0), window=self.image_display_c_frame, anchor=tk.NW)
        self.image_display_c_canvas.configure(scrollregion=self.image_display_c_canvas.bbox('all'))

        self.scrollbar_d = tk.Scrollbar(self.image_display_d, orient="vertical", command=self.image_display_d_canvas.yview)
        self.scrollbar_d.grid(row=0, column=1, sticky='ns')
        self.image_display_d_canvas.configure(yscrollcommand=self.scrollbar_d.set)
        self.image_display_d_frame = tk.Frame(self.image_display_d_canvas)
        self.image_display_d_frame.pack(fill="both", expand=True)
        self.image_display_d_canvas.create_window((0,0), window=self.image_display_d_frame, anchor=tk.NW)
        self.image_display_d_canvas.configure(scrollregion=self.image_display_d_canvas.bbox('all'))












        pathA = 'D:\\CS\\2023 HCM AI CHALLENGE\\keyframes\\L01_V021\\0077.jpg'
        imageA = Image.open(pathA).resize((160, 90), Image.LANCZOS)
        photoA = ImageTk.PhotoImage(imageA)

        labelA = tk.Label(self.image_display_a_frame, image=photoA)
        labelA.configure(image=photoA)
        labelA.image = photoA
        labelA.grid(row=0, column=0, padx=5, sticky='nsew')
        labelA.bind("<Button-1>", lambda e, path=pathA: self.on_image_click(path))   # chua hieu

        pathB = 'D:\\CS\\2023 HCM AI CHALLENGE\\keyframes\\L01_V021\\0078.jpg'
        imageB = Image.open(pathB).resize((160, 90), Image.LANCZOS)
        photoB = ImageTk.PhotoImage(imageB)

        labelB = tk.Label(self.image_display_a_frame, image=photoB)
        labelB.configure(image=photoB)
        labelB.image = photoB
        labelB.grid(row=0, column=1, padx=5, sticky='nsew')
        labelB.bind("<Button-1>", lambda e, path=pathB: self.on_image_click(path))   # chua hieu

        pathC = 'D:\\CS\\2023 HCM AI CHALLENGE\\keyframes\\L01_V021\\0079.jpg'
        imageC = Image.open(pathC).resize((160, 90), Image.LANCZOS)
        photoC = ImageTk.PhotoImage(imageC)

        labelC = tk.Label(self.image_display_a_frame, image=photoC)
        labelC.configure(image=photoC)
        labelC.image = photoC
        labelC.grid(row=1, column=0, padx=5, sticky='nsew')
        labelC.bind("<Button-1>", lambda e, path=pathC: self.on_image_click(path))   # chua hieu




        


if __name__ == "__main__":
    

    # set up data
    # dataset = fo.Dataset.from_images_dir('D:\\CS\\2023 HCM AI CHALLENGE\\keyframes', name=None, tags=None, recursive=True)
    dataset = fo.load_dataset('aic2023-kf-1')

    root = tk.Tk()
    app = ImageApp(root, dataset)
    
    # session = fo.launch_app(dataset, desktop=True)
    

    root.mainloop()
