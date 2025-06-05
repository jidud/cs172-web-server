import os
from flask import Flask, render_template, request
from simple_search import search 
from lucene_indexer import index_jsonl_or_folder

# Initialize Flask app
app = Flask(__name__)

# display search form
@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    results = []

    if request.method == "POST":
        query = request.form.get("query")
        if query:
            # using search from simple_serach
            results = search("/home/cs172/index", query)
    
    return render_template("index.html", query=query, results=results)


@app.route("/index", methods=["POST"])
def index_data():
    data_path = request.form.get("data_path")
    index_dir = "/home/cs172/index"  # directory
    
    if not data_path:
        return "Data path not provided", 400

    # index data
    try:
        index_jsonl_or_folder(data_path, index_dir)
    except Exception as e:
        return f"An error occurred during indexing: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
