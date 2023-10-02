from paddleocr import PaddleOCR, draw_ocr

import os
import sys
import subprocess

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

import cv2
import copy
import numpy as np
import json
import time
import logging
from PIL import Image
import tools.infer.utility as utility
import tools.infer.predict_rec as predict_rec
import tools.infer.predict_det as predict_det
import tools.infer.predict_cls as predict_cls
from ppocr.utils.utility import get_image_file_list, check_and_read
from ppocr.utils.logging import get_logger
from tools.infer.utility import draw_ocr_box_txt, get_rotate_crop_image, get_minarea_rect_crop
logger = get_logger()

from tools.infer.predict_system import main

# lenh de chay cai python nay
# de y la phai cd ocr/paddle-ocr

# python test-ocr.py --use_gpu=False --det_model_dir="inference/det" --det_algorithm="DB++" --rec_model_dir="inference/rec" --rec_algorithm="SPIN" --rec_image_shape="3,32,320" --drop_score=0.001 --rec_char_dict_path="./vietnamese-dict.txt" --use_space_char=False --vis_font_path=font-times-new-roman.ttf --show_log=False --text_folder="H:\AI_CHALLENGE\Text" --folder_path="H:\AI_CHALLENGE\Keyframes\Keyframes_L01\keyframes"
# xai cai nay ne # python ocr/paddle-ocr/test-ocr.py --use_gpu=True --det_model_dir="/kaggle/input/inference/inference/det" --det_algorithm="DB++" --rec_model_dir="/kaggle/input/inference/inference/rec" --rec_algorithm="SPIN" --rec_image_shape="3,32,320" --drop_score=0.001 --rec_char_dict_path="/kaggle/working/2023-ai-challenge/ocr/paddle-ocr/vietnamese-dict.txt" --use_space_char=False --vis_font_path=font-times-new-roman.ttf --show_log=False --text_folder="/kaggle/working/text" --folder_path="/kaggle/input/keyframes-l05"
# Thu muc luu cac file ocr
text_folder = "H:\\AI_CHALLENGE\\Text"

# # ocr cac part video tu part_left den part_right - 1 va cac video tu video_left den video_right - 1
# def process_folders(args, part_left, part_right, video_left, video_right):
#     for i in range(part_left, part_right):  # Loop from 1 to 20
#         folder_suffix = f"{i:02}"  # Format i with a leading zero if needed
#         folder_path = f"H:\\AI_CHALLENGE\\Keyframes\\Keyframes_L{folder_suffix}\\keyframes"
        
#         if os.path.exists(folder_path) and os.path.isdir(folder_path):
#             # Get a list of all folders in the specified directory
#             folder_names = os.listdir(folder_path)
            
#             for folder_name in folder_names[video_left-1:video_right-1]:
#                 folder_full_path = os.path.join(folder_path, folder_name)
                
#                 if os.path.isdir(folder_full_path):
#                     # Call your custom function with the folder_full_path
#                     process_folder(args, folder_full_path)

def process_folders(args, folder_path):
    
    folder_names = os.listdir(folder_path)
            
    for folder_name in folder_names:
        folder_full_path = os.path.join(folder_path, folder_name)

        if os.path.isdir(folder_full_path):
            # Call your custom function with the folder_full_path
            process_folder(args, folder_full_path)

# ocr cho thu muc folder_name
def process_folder(args, folder_name):
    print(f"Processing folder: {folder_name}")

    folder_parts = folder_name.split("\\")
    last_part = folder_parts[-1]
    output_folder = args.text_folder

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print(f"Output folder: {output_folder}")

    args.image_dir = folder_name
    res = main(args)

    for x in res:
        text_file = x['image_name'].split(".")[0] + '.txt'
        with open(output_folder + "/" + text_file, 'w', encoding='utf-8') as file:
            # Write content to the file if needed
            for str in x['transcriptions']:
                file.write(str + '\n')

# Call the process_folders function to start the processing
# process_folders(1, 4)

if __name__ == "__main__":
    args = utility.parse_args()
    if args.use_mp:
        p_list = []
        total_process_num = args.total_process_num
        for process_id in range(total_process_num):
            cmd = [sys.executable, "-u"] + sys.argv + [
                "--process_id={}".format(process_id),
                "--use_mp={}".format(False)
            ]
            p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stdout)
            p_list.append(p)
        for p in p_list:
            p.wait()
    else:
        # cur_folder = "H:\AI_CHALLENGE\Keyframes\Keyframes_L01\keyframes"
        # res = main(args)
        # for x in res:

        # ocr cac thu muc keyframe nam trong Keyframes_L01 den Keyframes_L02
        # va tren cac video V007 den V008 
        folder_path = args.folder_path
        process_folders(args, folder_path)

