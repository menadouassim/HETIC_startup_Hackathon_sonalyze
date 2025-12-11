from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import json, uuid

app = Flask(__name__, static_folder="static")
CORS(app)

# Folders
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ROOMS_DIR = DATA_DIR / "rooms"
ROOMS_DIR.mkdir(exist_ok=True)

SVG_DIR = Path("static/rooms")




# --- Serve index.html ---
@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")



from app import app

if __name__ == "__main__":
    app.run(debug=True)
