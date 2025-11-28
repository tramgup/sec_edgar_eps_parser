from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import parsing
import os
import tempfile


app = Flask(__name__)
CORS(app)

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file uploaded"}), 400

    files = request.files.getlist("file")

    temp_dir = tempfile.mkdtemp()
    uploaded_file_paths = []

    for file in files:
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        uploaded_file_paths.append(file_path)

    # Call parser on the folder
    result = parsing(temp_dir)  # your parser expects a folder

    return jsonify({"ok": True, "result": result})

if __name__ == "__main__":
    app.run(debug=True,port=5000)
