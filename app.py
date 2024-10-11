from flask import Flask, request, jsonify
from search import search
from filter import Filter
from storage import DBStorage
import html

app = Flask(__name__)

styles = """
<style>
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 20px;
        background-color: #121212;
        color: #e0e0e0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .header {
        text-align: center;
        margin-bottom: 40px;
        width: 100%;
    }
    .logo {
        font-size: 48px;
        font-weight: bold;
        color: #8ab4f8;
    }
    .search-container {
        width: 100%;
        max-width: 600px;
        margin-bottom: 20px;
    }
    .search-box {
        width: 100%;
        height: 50px;
        border: 1px solid #444;
        border-radius: 25px;
        padding: 0 20px;
        font-size: 18px;
        background-color: #1e1e1e;
        color: #e0e0e0;
        outline: none;
        box-sizing: border-box;
    }
    .search-box:hover, .search-box:focus {
        box-shadow: 0 1px 6px rgba(255,255,255,.2);
        border-color: rgba(255,255,255,0.5);
    }
    .search-button {
        background-color: #3a3a3a;
        border: none;
        border-radius: 24px;
        color: #e0e0e0;
        font-size: 16px;
        margin-top: 10px;
        padding: 10px 20px;
        cursor: pointer;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .search-button:hover {
        background-color: #575757;
    }
    .results-container {
        width: 100%;
        max-width: 600px;
    }
    .result {
        margin-bottom: 20px;
        padding: 10px;
        border-radius: 8px;
        background-color: #1e1e1e;
    }
    .site {
        font-size: 14px;
        color: #8ab4f8;
        margin: 0;
    }
    .title {
        font-size: 18px;
        color: #bb86fc;
        text-decoration: none;
        margin: 5px 0;
        display: block;
    }
    .title:hover {
        text-decoration: underline;
    }
    .snippet {
        font-size: 14px;
        color: #b0b0b0;
        margin: 5px 0 0 0;
    }
    .rel-button {
        cursor: pointer;
        color: #8ab4f8;
    }
    .rel-button:hover {
        text-decoration: underline;
    }
</style>
<script>
const relevant = function(query, link){
    fetch("/relevant", {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
           "query": query,
           "link": link
          })
      });
}
</script>
"""

search_template = styles + """
<div class="header">
    <div class="logo">Google Filter Search</div>
</div>
<div class="search-container">
    <form action="/" method="post">
        <input type="text" name="query" class="search-box" placeholder="Search...">
        <input type="submit" value="Search" class="search-button">
    </form>
</div>
<div class="results-container">
"""

result_template = """
<div class="result">
    <p class="site">{link} · <span class="rel-button" onclick='relevant("{query}", "{link}");'>Relevant</span></p>
    <a href="{link}" class="title">{title}</a>
    <p class="snippet">{snippet}</p>
</div>
"""

def show_search_form():
    return search_template + "</div>"

def run_search(query):
    results = search(query)
    fi = Filter(results)
    filtered = fi.filter()
    rendered = search_template
    filtered["snippet"] = filtered["snippet"].apply(lambda x: html.escape(x))
    
    for index, row in filtered.iterrows():
        rendered += result_template.format(**row)
    
    rendered += "</div>"
    return rendered

@app.route("/", methods=['GET', 'POST'])
def search_form():
    if request.method == 'POST':
        query = request.form["query"]
        return run_search(query)
    else:
        return show_search_form()

@app.route("/relevant", methods=["POST"])
def mark_relevant():
    data = request.get_json()
    query = data["query"]
    link = data["link"]
    
    storage = DBStorage()
    storage.update_relevance(query, link, 10)
    
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)