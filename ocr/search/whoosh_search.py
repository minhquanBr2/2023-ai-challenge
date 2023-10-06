from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir
from whoosh.query import FuzzyTerm
from mapping_keyframe import get_frame_info
from PIL import Image, ImageTk
import os

import sys
sys.path.insert(0, "D:\\University\\Contest\\AIChallenge\\2023-ai-challenge")
from GlobalLink import KeyframeFolder, OCRTextFolder, SubtitleTextFolder
from frame import VideoFrame
 


def search_text_ocr(query, topN):
    ix = open_dir("D:\\University\\Contest\\AIChallenge\\2023-ai-challenge\\indexdir")
    query_str = query
    searcher = ix.searcher(weighting=scoring.Frequency)
    query = QueryParser("content", ix.schema, termclass=FuzzyTerm).parse(query_str)
    results = searcher.search(query, limit=None)
    
    os.system('cls')
    output = []
    for i in range(min(topN, len(results))):
        path = results[i]['path'].replace(OCRTextFolder, KeyframeFolder).replace('txt', 'jpg')
        video_name = results[i]['video_name']
        keyframe_idx = results[i]['keyframe_idx']
        frame_idx = get_frame_info(video_name, keyframe_idx)
        image = None     
        videoFrame = VideoFrame(path, video_name, keyframe_idx, frame_idx, image, 0)
        output.append(videoFrame)
        print(path)
        print(f"{video_name}, {keyframe_idx}, {frame_idx}, ", results[i]['textdata'].replace('\n', ' '), '\n')
    
    print("Number of results:", len(output))
    return output

def search_text_subtitle(query, topN):
    ix = open_dir("D:\\University\\Contest\\AIChallenge\\2023-ai-challenge\\indexdirSubtitle")
    query_str = query
    searcher = ix.searcher(weighting=scoring.Frequency)
    query = QueryParser("content", ix.schema, termclass=FuzzyTerm).parse(query_str)
    results = searcher.search(query, limit=None)
    
    os.system('cls')
    output = []
    for i in range(min(topN, len(results))):
        path = ""        
        video_name = results[i]['video_name']
        keyframe_idx = ""
        frame_idx = results[i]['keyframe_idx'].split('_')[1].split('.')[0]
        image = None
        videoFrame = VideoFrame(path, video_name, keyframe_idx, frame_idx, image, 0)
        output.append(videoFrame)
        print(f"{video_name}, {keyframe_idx}, {frame_idx}, ", results[i]['textdata'].replace('\n', ' '), '\n')
    
    print("Number of results:", len(output))
    return output

if __name__ == "__main__":
    search_text_ocr(u"đại học quốc gia", 100)
