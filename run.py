from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import json, uuid
from app import app
app = Flask(__name__, static_folder="templates")
CORS(app)

# Folders


# --- Serve index.html ---
@app.get("/index")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/")
def landing():
    return send_from_directory(app.static_folder, "landing.html")
SVG_DIR=Path("static/rooms") 
@app.get("/rooms")
def get_room_templates():
    templates = []
    for svg_file in SVG_DIR.glob("*.html"):
        type_name = svg_file.stem
        svg_content = svg_file.read_text()
        templates.append({
            "type": type_name,
            "svg": svg_content,
            "width": 120,
            "height": 120
        })
    return jsonify({"rooms": templates})

if __name__ == "__main__":
    app.run(debug=True)
