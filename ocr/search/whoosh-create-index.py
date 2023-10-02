import os
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import RegexAnalyzer, LowercaseFilter, StopFilter, CharsetFilter


def createAccentMap(path):
    file = open(path, "r", encoding="utf-8")
    charmap = {}
    for char in file:
        char = char.strip()
        charmap[ord(char)] = char
    return charmap
 
def createSearchableData(root, path):   

    # map từ số nguyên sang kí tự tiếng Việt unicode
    charmap = createAccentMap(path)
    
    # analyzer giúp bỏ phân biệt chữ hoa chữ thường, bỏ stop-words, config charset của tiếng Việt 
    # https://stackoverflow.com/questions/42769299/whoosh-not-searching-words-with-accent
    accent_analyzer = RegexAnalyzer(r'\w+') | LowercaseFilter() \
                  | StopFilter() | CharsetFilter(charmap=charmap)
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), 
                    content=TEXT, textdata=TEXT(stored=True, analyzer=accent_analyzer))
    
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
 
    # Creating a index writer to add document as per schema
    ix = create_in("indexdir", schema)
    writer = ix.writer()
 
    filepaths = [os.path.join(root, i) for i in os.listdir(root)]
    for path in filepaths:
        fp = open(path, 'r', encoding="utf-8")
        print(path)
        text = fp.read()
        writer.add_document(title=path.split("\\")[1], path=path, content=text, textdata=text)
        fp.close()
    writer.commit()
 
root = "corpus"
path = "D:/VSCode/2023-ai-challenge/ocr/search/vietnamese-dict.txt"
createSearchableData(root, path)