from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import json, uuid
from app import app
app = Flask(__name__, static_folder="templates")
CORS(app)

# Folders
from flask import render_template ,request, jsonify


from pathlib import Path
import json, uuid
from scripts.json_parser import process_and_sample_folder
from scripts.llm_intermidiary import send_to_llm
from scripts.json_to_pdf import json_to_pdf
DATA_DIR=Path("data")
ROOMS_DIR=Path("data/rooms")
SVG_DIR = Path("static/rooms") 


# --- Save layout ---
@app.post("/layout/save")
def save_layout():
    payload = request.get_json()
    wrapper = {
        "id": str(uuid.uuid4()),
        "layout": payload.get("layout", [])
    }
    with open(DATA_DIR / "saved_layout.json", "w", encoding="utf-8") as f:
        json.dump(wrapper, f, indent=2)
    return jsonify({"status": "saved", "id": wrapper["id"]})

# --- Upload JSON per room ---
@app.post("/room/data")
def upload_room_json():
    try:
        room_id = request.form.get("room_id")
        file = request.files.get("file")
        if not room_id or not file:
            return jsonify({"error": "Missing room_id or file"}), 400

        out = ROOMS_DIR / f"{room_id}.json"
        print(room_id)
        file.save(out)
        return jsonify({"status": "stored", "room_id": room_id})
    except Exception as e:
        print(
            e
        )
        return jsonify({"error": str(e)}), 500


@app.route("/run-scripts", methods=["POST"])
def run_scripts():

    # Run in order — EACH one waits for the previous one to finish
    process_and_sample_folder()
    send_to_llm(export_path="exports/prompt_result/llm_resilt.json")
    json_to_pdf(file_path="exports/prompt_result/llm_resilt.json",export_path="exports/final_result/output.pdf")
    

    

    return jsonify({"status": "all done"})


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
