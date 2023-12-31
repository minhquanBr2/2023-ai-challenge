import os
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import RegexAnalyzer, LowercaseFilter, StopFilter, CharsetFilter
from glob import glob

import sys
sys.path.insert(0, "D:\\University\\Contest\\AIChallenge\\2023-ai-challenge")
from GlobalLink import OCRTextFolder, SubtitleTextFolder, VietnameseDict

def createAccentMap(path):
    file = open(path, "r", encoding="utf-8")
    charmap = {}
    for char in file:
        char = char.strip()
        charmap[ord(char)] = char
    return charmap
 
def createSearchableData(root, path, indexdir):   

    # map từ số nguyên sang kí tự tiếng Việt unicode
    charmap = createAccentMap(path)
    
    # analyzer giúp bỏ phân biệt chữ hoa chữ thường, bỏ stop-words, config charset của tiếng Việt 
    # https://stackoverflow.com/questions/42769299/whoosh-not-searching-words-with-accent
    accent_analyzer = RegexAnalyzer(r'\w+') | LowercaseFilter() \
                  | StopFilter() | CharsetFilter(charmap=charmap)
    schema = Schema(path = TEXT(stored=True), video_name=TEXT(stored=True), keyframe_idx=TEXT(stored=True), 
                    content=TEXT, textdata=TEXT(stored=True, analyzer=accent_analyzer))
    
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
 
    # Creating a index writer to add document as per schema
    ix = create_in(indexdir, schema)
    writer = ix.writer()
 
    # filepaths = [os.path.join(root, i) for i in os.listdir(root)]
    folders = glob(root + '\\*\\')
    for folder in folders:
        print(folder)
        filepaths = glob(folder + '*.txt')
        for path in filepaths:
            fp = open(path, 'r', encoding="utf-8")
            text = fp.read()
            writer.add_document(path=path,
                                video_name=path.split("\\")[-2], 
                                keyframe_idx=path.split("\\")[-1][:-4], 
                                content=text, 
                                textdata=text)
            fp.close()
    writer.commit()
 
root = OCRTextFolder
path = VietnameseDict
createSearchableData(root, path, "indexdir")

root = SubtitleTextFolder
path = VietnameseDict
createSearchableData(root, path, "indexdirSubtitle")