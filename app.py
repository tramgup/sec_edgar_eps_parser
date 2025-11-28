from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile


app = Flask(__name__)
CORS(app)

def process_file(file_path):
    #do processing

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file uploaded"}), 400

    file = request.files["file"]

    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.filename)
    file.save(file_path)

    result = process_file(file_path)

    return jsonify({"ok": True, "result": result})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
