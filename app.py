from flask import Flask, render_template, request, jsonify, session
from models.image_captioning import load_captioning_model, generate_caption
from models.object_detection import load_yolo_model, detect_objects
from models.color_recognition import extract_dominant_colors
from werkzeug.utils import secure_filename
import os
import logging
import speech_recognition as sr
import pyttsx3
from PIL import Image
import numpy as np
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configurations
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Load Models
logging.info("Loading models...")
caption_processor, caption_model = load_captioning_model()
yolo_model = load_yolo_model()
nlp_query_processor = pipeline("question-answering")  # Hugging Face for query handling
logging.info("Models loaded successfully.")

# Initialize Text-to-Speech engine
tts_engine = pyttsx3.init()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def text_to_speech(text):
    """Convert text to speech."""
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        logging.error(f"Error in text-to-speech: {e}")

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    """Handle image upload and object detection."""
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Process image properly
        image = Image.open(filepath).convert("RGB")
        image_np = np.array(image)  # Convert PIL Image to NumPy array

        # Object detection
        objects = detect_objects(yolo_model, image_np)

        # Color recognition (Convert tuples to strings)
        colors = extract_dominant_colors(image)
        colors = [str(color) for color in colors]  # Ensure all elements are strings

        # Generate caption
        caption = generate_caption(caption_processor, caption_model, image)

        # Store image details in session
        session["last_image"] = {
            "objects": objects,
            "colors": colors,
            "image_url": filepath,
            "filename": filename,
            "caption": caption
        }

        return jsonify({"objects": objects, "colors": colors, "image_url": filepath, "caption": caption})
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return jsonify({"error": "An error occurred while processing the image."}), 500

@app.route("/query", methods=["POST"])
def image_query():
    """Process user queries about the uploaded image."""
    if "last_image" not in session:
        return jsonify({"error": "No image uploaded yet."}), 400

    try:
        data = request.json
        user_query = data.get("message", "").lower()

        if not user_query:
            return jsonify({"error": "Invalid input"}), 400

        # Retrieve stored image details
        image_info = session["last_image"]
        caption = image_info.get("caption", "No caption generated yet.")
        objects = ", ".join(image_info["objects"]) if image_info["objects"] else "No objects detected."
        colors = ", ".join(image_info["colors"]) if image_info["colors"] else "No colors detected."

        # Convert the list of colors to actual color names if they are not already
        if colors:
            # Assuming colors are already in string form (e.g., 'red', 'green', etc.)
            color_names = colors
        else:
            color_names = "No colors detected."

        # Determine response using NLP-based processing
        response = ""
        if "what is this" in user_query or "what is in the image" in user_query:
            response = f"📸: {caption}"
        elif "what color" in user_query or "which color" in user_query:
            response = f"🎨: {color_names}"
        else:
            try:
                nlp_response = nlp_query_processor({
                    "question": user_query,
                    "context": f"Caption: {caption}. Objects: {objects}. Colors: {color_names}."
                })
                response = nlp_response.get("answer", "I am unsure about that.")
            except Exception as e:
                logging.error(f"NLP Processing Error: {e}")
                response = "⚠️ I couldn't understand the question."

        text_to_speech(response)
        return jsonify({"reply": response})
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({"error": "An error occurred."}), 500
if __name__ == "__main__":
    app.run(debug=True)
