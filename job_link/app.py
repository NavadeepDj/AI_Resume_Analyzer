import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files or 'job_role' not in request.form:
        return jsonify({"error": "Resume and job role are required"}), 400

    job_role = request.form['job_role'].strip().replace(" ", "+")  # Format for URL

    # Generate exact job links dynamically
    job_links = {
        "LinkedIn Jobs": f"https://www.linkedin.com/jobs/search/?keywords={job_role}",
        "Indeed Jobs": f"https://www.indeed.com/jobs?q={job_role}",
        "Glassdoor Jobs": f"https://www.glassdoor.com/Job/{job_role}-jobs-SRCH_KO0,16.htm"
    }

    return jsonify({"job_links": job_links})

if __name__ == '__main__':
    app.run(debug=True)
