from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh.index import open_dir
from whoosh.query import FuzzyTerm
import sys
 
ix = open_dir("indexdir")
 
# query_str is query string
query_str = sys.argv[1]
# Top 'n' documents as result
topN = int(sys.argv[2])

searcher = ix.searcher(weighting=scoring.TF_IDF)
query = QueryParser("content", ix.schema, termclass=FuzzyTerm).parse(query_str)
results = searcher.search(query)
print(results)

for i in range(min(topN, len(results))):
    print(results[i]['title'], str(results[i].score), results[i]['textdata'])
