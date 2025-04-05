from flask import Flask, request, jsonify, render_template
import os
import numpy as np
import faiss
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

app = Flask(__name__)
YOUR_DISTANCE_THRESHOLD = 0.5  # Adjust this value based on your model's output
# Initialize MTCNN and Inception ResNet model
mtcnn = MTCNN(keep_all=True, device='cuda' if torch.cuda.is_available() else 'cpu')
model = InceptionResnetV1(pretrained='vggface2').eval().to('cuda' if torch.cuda.is_available() else 'cpu')

# Function to extract face embeddings
def get_face_embedding(image_path):
    img = Image.open(image_path)
    img_cropped = mtcnn(img)
    if img_cropped is not None:
        img_embedding = model(img_cropped).detach().cpu().numpy()
        return img_embedding
    return None

# Build FAISS index from the image database
def build_faiss_index(image_database_path):
    embeddings = []
    image_paths = []

    for img_name in os.listdir(image_database_path):
        img_path = os.path.join(image_database_path, img_name)
        embedding = get_face_embedding(img_path)
        if embedding is not None:
            embeddings.append(embedding[0])  # Use the first face detected
            image_paths.append(img_path)

    # Convert to numpy array
    embeddings = np.array(embeddings).astype('float32')

    # Create a FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 distance
    index.add(embeddings)  # Add embeddings to the index

    return index, image_paths

# Search for similar faces
def search_similar_faces(uploaded_image_path, index, image_paths):
    uploaded_embedding = get_face_embedding(uploaded_image_path)
    if uploaded_embedding is not None:
        uploaded_embedding = uploaded_embedding[0].reshape(1, -1).astype('float32')
        
        # Get the number of images in the database
        num_images_in_db = len(image_paths)
        
        # Perform the search, but limit k to the number of images in the database
        k = min(5, num_images_in_db)  # Only search for as many as exist
        distances, indices = index.search(uploaded_embedding, k=k)  # Get top k matches

        # Create a list to hold the results
        results = []
        for j, i in enumerate(indices[0]):
            if i < num_images_in_db:  # Ensure the index is valid
                # Check if the image is similar (you can define a threshold for similarity)
                # For example, if the distance is below a certain threshold, consider it similar
                if distances[0][j] < YOUR_DISTANCE_THRESHOLD:  # Set a threshold value
                    results.append((f"/static/image_database/{os.path.basename(image_paths[i])}", float(distances[0][j])))

        return results  # Return only the valid matches
    return []
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded selfie
    uploaded_image_path = os.path.join('uploads', file.filename)
    file.save(uploaded_image_path)

    # Build the FAISS index from the image database
    index, image_paths = build_faiss_index('static/image_database')

    # Search for similar faces
    similar_faces = search_similar_faces(uploaded_image_path, index, image_paths)

    # Return results
    if similar_faces:
        return jsonify({"matches": similar_faces})
    else:
        return jsonify({"message": "No similar faces found."})
@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(debug=True,port=5009)