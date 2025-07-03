from flask import Flask, request, jsonify, send_file, session, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import datetime
import traceback 
import os
import re
from AudioStegnographyAlgo.LSBAudioStego import LSBAudioStego
from AudioStegnographyAlgo.PhaseEncodingAudioStego import PhaseEncodingAudioStego

# Initialize Flask app

app = Flask(__name__)

app = Flask(__name__, static_folder="frontend", template_folder="frontend")
 
CORS(app)  # Enable CORS for frontend communication

# =================== DATABASE CONFIG ===================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# =================== FIXED DOWNLOAD PATH ===================
DOWNLOAD_PATH = r"C:\Users\MADHU\Downloads"

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

# =================== USER MODEL ===================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# =================== DATABASE CREATION ===================
with app.app_context():
    try:
        db.create_all()  # Ensure all tables exist
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")

 # =================== SERVE FORGOT PASSWORD PAGE ===================
@app.route("/forgot")
def forgot_password_page():
    return render_template("forgot.html")

# =================== RESET PASSWORD API ===================
@app.route("/reset-password", methods=["POST"])
def reset_password():
    try:
        data = request.get_json()
        email = data.get("email")
        new_password = data.get("newPassword")

        if not email or not new_password:
            return jsonify({"error": "Email and new password are required."}), 400

        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({"error": "Invalid email format."}), 400

        # Validate new password (must contain at least one number and one special character)
        if not re.match(r'^(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]+$', new_password):
            return jsonify({"error": "Password must contain at least one number and one special character."}), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"error": "User not found."}), 404

        # Hash the new password
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        return jsonify({"message": "Password reset successful!"}), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# =================== SIGNUP API ===================
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        # Validate username (allow letters and numbers only)
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            return jsonify({"error": "Username can only contain letters and numbers"}), 400

        # Validate email (must contain @ and a domain)
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password (must contain at least one number and one special character)
        if not re.match(r'^(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]+$', password):
            return jsonify({"error": "Password must contain at least one number and one special character"}), 400

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({"error": "Username or Email already exists"}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        print(f"❌ Error in signup: {str(e)}")  # Logs the actual error
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    
    # =================== LOGIN API ===================
@app.route("/index", methods=["POST"])
def login():
    try:
        data = request.get_json()
        user_identifier = data.get("user_identifier")
        password = data.get("password")

        if not user_identifier or not password:
            return jsonify({"error": "Username or Email and password are required"}), 400

        user = User.query.filter((User.username == user_identifier) | (User.email == user_identifier)).first()
        if not user:
            return jsonify({"error": "User does not exist"}), 400

        if bcrypt.check_password_hash(user.password, password):
            return jsonify({"message": "Login successful", "username": user.username}), 200
        else:
            return jsonify({"error": "Incorrect password"}), 400

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    
    
    
# =================== AUDIO STEGANOGRAPHY APIs ===================
@app.route("/encode", methods=["POST"])
def encode():
    if "file" not in request.files or "message" not in request.form or "algorithm" not in request.form:
        return jsonify({"error": "Missing file, message, or algorithm"}), 400

    file = request.files["file"]
    message = request.form["message"]
    algorithm = request.form["algorithm"].lower()

    try:
        if algorithm == "lsb":
            algo = LSBAudioStego()
        elif algorithm == "phase":
            algo = PhaseEncodingAudioStego()
        else:
            return jsonify({"error": "Invalid algorithm. Use 'lsb' or 'phase'."}), 400

        # Save the uploaded file temporarily
        temp_file_path = os.path.join(DOWNLOAD_PATH, file.filename)
        file.save(temp_file_path)  # Save file before encoding

        # Perform encoding with the saved file path
        encoded_file_path = algo.encodeAudio(temp_file_path, message)

        if not os.path.exists(encoded_file_path):
            return jsonify({"error": "Encoding failed: Output file not created."}), 500

        return jsonify({
            "message": "Encoding successful!",
            "file": os.path.basename(encoded_file_path),
            "download_url": f"http://127.0.0.1:5000/download/{os.path.basename(encoded_file_path)}"
        })
    
    except Exception as e:
        traceback.print_exc()  # Print full error to console
        return jsonify({"error": f"Encoding failed: {str(e)}"}), 500


@app.route("/decode", methods=["POST"])
def decode():
    if "file" not in request.files or "algorithm" not in request.form:
        return jsonify({"error": "Missing file or algorithm"}), 400

    file = request.files["file"]
    algorithm = request.form["algorithm"].lower()

    try:
        if algorithm == "lsb":
            algo = LSBAudioStego()
        elif algorithm == "phase":
            algo = PhaseEncodingAudioStego()
        else:
            return jsonify({"error": "Invalid algorithm. Use 'lsb' or 'phase'."}), 400

        decoded_message = algo.decodeAudio(file)
        if not decoded_message:
            return jsonify({"error": "Decoding failed: No message extracted."}), 500

        return jsonify({"message": decoded_message})
    
    except Exception as e:
        return jsonify({"error": f"Decoding failed: {str(e)}"}), 500

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_PATH, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)

