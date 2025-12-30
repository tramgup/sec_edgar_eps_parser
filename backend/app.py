from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from parser import parsing
import os
import tempfile
import uuid
import shutil
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from threading import Thread
import time



app = Flask(__name__)
CORS(app, origins=[os.environ['FRONTEND_PUBLIC_DOMAIN']])

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 #50MB max upload

# used for storing session data temporarily
sessions = {}

#limit requests
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)


# user uploads all of the html files they want to analyze
@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file uploaded"}), 400

    files = request.files.getlist("file")

    # create a unique session id for this upload.
    session_id = str(uuid.uuid4())

    temp_dir = tempfile.mkdtemp()
    uploaded_file_paths = []

    for file in files:
        filename = file.filename.lower()
        
        #validating only .html can be sent
        if not filename.endswith("html") or not filename.endswith("htm"):
            return jsonify({"ok": False, "error": f"Invalid file type: {filename}. Only .html allowed."}), 400
        
        # checking MIME type, more secure
        if file.mimetype not in ["text/html"]:
            return jsonify({"ok": False, "error": f"Invalid MIME type for {filename}"}), 400

 
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        uploaded_file_paths.append(file_path)
    
    # Create unique output CSV path for this session
    output_csv = os.path.join(tempfile.gettempdir(), f"eps_output_{session_id}.csv")
    
    # Store session info
    sessions[session_id] = {
        "output_csv": output_csv,
        "temp_dir": temp_dir,
        "created_at": time.time()
    }

    # Call parser on the folder
    result = parsing(temp_dir, output_csv)  # your parser expects a folder

    return jsonify({
        "ok": True, 
        "result": result,
        "session_id": session_id  # Send back to client
    })

# user can download a csv file containing the linkings for large data analysis
@app.route("/api/download/<session_id>", methods=["GET"])
def download_analyzed_file(session_id):
    if session_id not in sessions:
        return jsonify({"ok": False, "error": "Session not found or expired"}), 404
    
    output_csv = sessions[session_id]["output_csv"]
    
    if not os.path.exists(output_csv):
        return jsonify({"ok": False, "error": "CSV file not found"}), 404
    
    return send_file(output_csv, as_attachment=True, download_name="eps_output.csv")

#cleaning up old user sessions
def cleanup_old_sessions(session_id):
    if not session_id:
        return
    try:
        if os.path.exists(sessions[session_id]["temp_dir"]):
            shutil.rmtree(sessions[session_id]["temp_dir"])
        if os.path.exists(sessions[session_id]["output_csv"]):
            os.remove(sessions[session_id]["output_csv"])
    except Exception as e:
        print(f"cleanup error: {e}")
    finally:
        del sessions[session_id]

def background_cleanup():
    """Clean up old sessions every 30 minutes"""
    while True:
        time.sleep(1800)  # 30 minutes
        current_time = time.time()
        
        for session_id in list(sessions.keys()):
            session_age = current_time - sessions[session_id].get("created_at", 0)
            if session_age > 7200:  # 2 hours
                cleanup_old_sessions(session_id)
                print(f"Cleaned up expired session: {session_id}")

# Start background thread when app starts
cleanup_thread = Thread(target=background_cleanup, daemon=True)
cleanup_thread.start()



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
    