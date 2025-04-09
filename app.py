import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import shutil
from PIL import Image
import numpy as np
import torch
import faiss
from facenet_pytorch import MTCNN, InceptionResnetV1

# Initialize Flask
app = Flask(__name__, static_folder='static')
CORS(app)

# Ensure required directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/image_database', exist_ok=True)
os.makedirs('static/final_photos', exist_ok=True)

# FaceNet models
device = 'cuda' if torch.cuda.is_available() else 'cpu'
mtcnn = MTCNN(keep_all=True, device=device)
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)

YOUR_DISTANCE_THRESHOLD = 0.5  # Adjust as needed


# === UTILITIES ===

def get_face_embedding(image_path):
    img = Image.open(image_path).convert('RGB')
    img_cropped = mtcnn(img)
    if img_cropped is not None:
        img_embedding = model(img_cropped).detach().cpu().numpy()
        return img_embedding
    return None

def build_faiss_index(image_database_path):
    embeddings = []
    image_paths = []

    for root, _, files in os.walk(image_database_path):  # Recursively walk through subfolders
        for file in files:
            if not file.lower().endswith(('.png', '.jpg', '.jpeg')):  # Optional: only image files
                continue

            img_path = os.path.join(root, file)
            try:
                embedding = get_face_embedding(img_path)
                if embedding is not None:
                    embeddings.append(embedding[0])
                    image_paths.append(img_path)
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                continue

    if not embeddings:
        return None, []

    embeddings = np.array(embeddings).astype('float32')
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return index, image_paths


def search_similar_faces(uploaded_image_path, index, image_paths):
    uploaded_embedding = get_face_embedding(uploaded_image_path)
    if uploaded_embedding is None:
        return []

    uploaded_embedding = uploaded_embedding[0].reshape(1, -1).astype('float32')
    k = min(5, len(image_paths))
    distances, indices = index.search(uploaded_embedding, k=k)

    results = []
    for j, i in enumerate(indices[0]):
        if distances[0][j] < YOUR_DISTANCE_THRESHOLD:
            matched_path = image_paths[i]
            final_path = os.path.join('static/final_photos', os.path.basename(matched_path))
            shutil.copy(matched_path, final_path)  # Copy to final_photos
            results.append({
                "path": f"/static/final_photos/{os.path.basename(matched_path)}",
                "distance": float(distances[0][j])
            })

    return results


# === ROUTES ===

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    if 'images' not in request.files:
        return jsonify({'error': 'No files found'}), 400

    files = request.files.getlist('images')

    # Clear the old database
    shutil.rmtree('static/image_database')
    os.makedirs('static/image_database', exist_ok=True)

    for file in files:
        if file and file.filename:
            rel_path = file.filename.replace("\\", "/")  # Normalize path for subfolders
            save_path = os.path.join('static/image_database', rel_path)

            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            file.save(save_path)


    return jsonify({'message': 'Folder uploaded successfully', 'file_count': len(files)})


@app.route('/upload_selfie', methods=['POST'])
def upload_selfie():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Clear previous results
    shutil.rmtree('static/final_photos')
    os.makedirs('static/final_photos', exist_ok=True)

    uploaded_path = os.path.join('uploads', file.filename)
    file.save(uploaded_path)

    index, image_paths = build_faiss_index('static/image_database')
    if index is None:
        return jsonify({"error": "No valid faces found in image database"}), 400

    matches = search_similar_faces(uploaded_path, index, image_paths)

    if not matches:
        return jsonify({"message": "No similar faces found."})

    return jsonify({"matches": matches})


if __name__ == '__main__':
    app.run(debug=True, port=5009)
    