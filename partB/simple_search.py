import sys
import lucene
import os
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.analysis.standard import StandardAnalyzer

_vm = None
_vm_started = False

def ensure_lucene_vm():
    global _vm, _vm_started
    if not _vm_started:
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        _vm = lucene.getVMEnv()
        _vm_started = True

def search(index_dir, q, top_n=10):
    ensure_lucene_vm()
    _vm.attachCurrentThread()
    directory = SimpleFSDirectory(Paths.get(index_dir))
    reader = DirectoryReader.open(directory)
    searcher = IndexSearcher(reader)
    analyzer = StandardAnalyzer()
    parser = QueryParser("body", analyzer)
    query = parser.parse(q)
    hits = searcher.search(query, top_n)
    results = []
    for scoreDoc in hits.scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        title = doc.get("title")
        url = doc.get("url")
        score = scoreDoc.score
        results.append((title, url, score))
    reader.close()
    return results
