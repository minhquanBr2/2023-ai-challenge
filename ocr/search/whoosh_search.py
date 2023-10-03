from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir
from whoosh.query import FuzzyTerm
import sys
 


def search_text_ocr(query, topN):
    ix = open_dir(".\\ocr\\search\\indexdir")
    query_str = query
    searcher = ix.searcher(weighting=scoring.Frequency)
    query = QueryParser("content", ix.schema, termclass=FuzzyTerm).parse(query_str)
    results = searcher.search(query, limit=None)
    
    out_result = []
    for i in range(min(topN, len(results))):
        out_result.append((results[i]['path'], results[i]['video_name'], results[i]['keyframe_idx']))

    
    print("Number of results:", len(results))
    return out_result
    # for i in range(min(topN, len(results))):
    #     (results[i]['video_name'], results[i]['keyframe_idx'], str(results[i].score), results[i]['textdata'])

if __name__ == "__main__":
    search_text_ocr(u"bánh tráng", 100)
