import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    # Check if a resume file is provided
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400

    # Save the uploaded file temporarily
    resume_file = request.files['resume']
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    temp_file_path = os.path.join(uploads_dir, resume_file.filename)
    resume_file.save(temp_file_path)

    try:
        # Initialize the Gemini client with your API key
        client = genai.Client(api_key="AIzaSyDsJoGTYCQUJdfv7MQlYO5TXfau96N5Qcs")
        
        # Upload the file to Gemini's file service
        file_response = client.files.upload(file=temp_file_path)

        model = "gemini-2.0-pro-exp-02-05"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=file_response.uri,
                        mime_type=file_response.mime_type,
                    ),
                    types.Part.from_text(
                        text="""analyze resumes and provide feedback on formatting, skill gaps, and suggestions for improvement.
Based on resume analysis, the system should recommend courses or learning paths to help users enhance their skills for better job prospects"""
                    ),
                ],
            )]
#             # Optionally you can provide a model output example or context
#             types.Content(
#                 role="model",
#                 parts=[
#                     types.Part.from_text(
#                         text="""Okay, I understand. Based on the OCR text and the image you provided, here's a breakdown of the resume content and potential analysis points:
# [Detailed analysis and feedback would appear here...]"""
#                     ),
#                 ],
#             ),
#             # If you have additional user instructions, you can include them here
#             types.Content(
#                 role="user",
#                 parts=[
#                     types.Part.from_text(text="""INSERT_INPUT_HERE"""),
#                 ],
#             ),
#         ]

        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=64,
            max_output_tokens=8192,
            response_mime_type="application/json",
        )

        output_text = ""
        # Stream the response from the model
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            output_text += chunk.text

        return jsonify({"feedback": output_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == '__main__':
    app.run(debug=True)
