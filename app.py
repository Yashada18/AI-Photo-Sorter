from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/') 
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def uploadFile():
    if 'images' not in request.files:
        return jsonify({'error': 'File not found'}), 400
    
    files = request.files.getlist('images')
    saved_files = []
    for file in files:
        if file.filename == '':
            continue
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        saved_files.append(file.filename)
        
        if not saved_files:
            return jsonify({'error': 'No File Uploaded'}), 400
        
    return jsonify({'message': 'Upload Successful', 'files': saved_files})


if __name__ == '__main__':
    app.run(debug=True)