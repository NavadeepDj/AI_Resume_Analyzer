import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

genai_api_key = "YOUR_VALID_GENAI_API_KEY"
genai.configure(api_key=genai_api_key)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400

    resume_file = request.files['resume']
    temp_file_path = os.path.join(UPLOAD_FOLDER, resume_file.filename)
    resume_file.save(temp_file_path)

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")

        with open(temp_file_path, "rb") as file:
            resume_content = file.read().decode("utf-8", errors="ignore")  # Handle encoding issues

        prompt = f"""
        You are an expert AI resume analyzer. Analyze the following resume and provide structured feedback in JSON format.

        Resume Content:
        {resume_content}

        Ensure output follows this structure:
        [
          {{ "resume_section": "header", "content": "...", "suggestions": ["..."] }},
          {{ "resume_section": "about_me", "content": "...", "suggestions": ["..."] }},
          ...
        ]
        """

        response = model.generate_content([prompt])

        if not response:
            return jsonify({"error": "AI model did not return a response"}), 500

        if hasattr(response, "text") and response.text.strip():
            print("AI Response:", response.text)  # Debugging log
            try:
                formatted_response = json.loads(response.text)  # Parse JSON safely
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON from AI"}), 500
        else:
            return jsonify({"error": "Empty AI response"}), 500

        return jsonify(formatted_response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == '__main__':
    app.run(debug=True)
