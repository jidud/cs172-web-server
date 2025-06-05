import os
import json
import lucene
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriterConfig, IndexWriter
from org.apache.lucene.document import Document, TextField, StringField
from org.apache.lucene.document import Field


def index_jsonl_or_folder(data_path, index_dir):
    # # Initialize the Lucene VM
    lucene.initVM()

    # Open/create the index directory
    store = SimpleFSDirectory(Paths.get(index_dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    writer = IndexWriter(store, config)

    # Collect files: either a folder of JSON/JSONL or a single file
    paths = []
    if os.path.isdir(data_path):
        for root, _, files in os.walk(data_path):
            for fn in files:
                if fn.lower().endswith(('.json', '.jsonl')):
                    paths.append(os.path.join(root, fn))
    elif os.path.isfile(data_path):
        paths = [data_path]
    else:
        raise ValueError(f"No such file or directory: {data_path}")

    # Iterate and index each document
    for path in paths:
        ext = os.path.splitext(path)[1].lower()
        docs = []
        if ext == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    docs = [json.load(f)]
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON: {path}")
                    continue
        elif ext == '.jsonl':
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        docs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        else:
            continue

        for doc_json in docs:
            # Create a Lucene document
            doc = Document()

            # Extract fields
            title = doc_json.get('title', '')
            url = doc_json.get('url', '')
            content = doc_json.get('content', '')
            metadata = doc_json.get('metadata', {})
            published = metadata.get('published_date', 'Unknown')
            author = metadata.get('author', 'Unknown')
            source = metadata.get('source', 'Unknown')

            # File creation timestamp
            try:
                ctime = os.path.getctime(path)
                import datetime
                created = datetime.datetime.fromtimestamp(ctime).isoformat()
            except:
                created = 'Unknown'

            # Add fields to the document
            doc.add(TextField('title', title, Field.Store.YES))
            doc.add(StringField('url', url, Field.Store.YES))
            doc.add(TextField('body', content, Field.Store.YES))
            doc.add(StringField('published_date', published, Field.Store.YES))
            doc.add(StringField('author', author, Field.Store.YES))
            doc.add(StringField('source', source, Field.Store.YES))
            doc.add(StringField('created_date', created, Field.Store.YES))

            writer.addDocument(doc)
            print(f"Indexed document from {path}")

    # Commit and close
    writer.commit()
    writer.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 lucene_indexer.py <path_to_json_or_folder> <path_to_index_dir>")
        sys.exit(1)

    data_directory = sys.argv[1]
    index_directory = sys.argv[2]
    index_jsonl_or_folder(data_directory, index_directory)
    print("Indexing complete.")
