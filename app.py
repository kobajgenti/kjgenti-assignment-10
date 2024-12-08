from flask import Flask, render_template, request, jsonify, send_from_directory
import torch
import torch.nn.functional as F
import open_clip
import pickle
from PIL import Image
import os

app = Flask(__name__)

# Configure directories
IMAGES_DIR = 'coco_images_resized'
UPLOAD_FOLDER = 'static/uploads'
DEMO_FOLDER = 'static/demo'

# Create necessary folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DEMO_FOLDER, exist_ok=True)

# Load model and tokenizer
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B/32', pretrained='openai')
tokenizer = open_clip.get_tokenizer('ViT-B-32')
model.eval()

# Load embeddings
with open('image_embeddings.pickle', 'rb') as f:
    df = pickle.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        query_type = data['queryType']
        text_query = data['textQuery']
        image_path = data.get('imagePath')
        lambda_val = float(data['lambda'])
        
        # Process queries
        if query_type == 'text':
            text = tokenizer([text_query])
            query_embedding = F.normalize(model.encode_text(text))
        elif query_type == 'image':
            try:
                # Try different directories in order
                possible_paths = [
                    os.path.join(IMAGES_DIR, image_path),
                    os.path.join(UPLOAD_FOLDER, image_path),
                    os.path.join(DEMO_FOLDER, image_path),
                    os.path.join('static', image_path)
                ]
                
                image_full_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        image_full_path = path
                        break
                
                if image_full_path is None:
                    return jsonify({'error': f'Image not found: {image_path}'}), 404
                
                image = preprocess(Image.open(image_full_path)).unsqueeze(0)
                query_embedding = F.normalize(model.encode_image(image))
            except Exception as e:
                return jsonify({'error': f'Error processing image: {str(e)}'}), 500
        else:  # hybrid
            text = tokenizer([text_query])
            text_embedding = F.normalize(model.encode_text(text))
            try:
                possible_paths = [
                    os.path.join(IMAGES_DIR, image_path),
                    os.path.join(UPLOAD_FOLDER, image_path),
                    os.path.join(DEMO_FOLDER, image_path),
                    os.path.join('static', image_path)
                ]
                
                image_full_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        image_full_path = path
                        break
                
                if image_full_path is None:
                    return jsonify({'error': f'Image not found: {image_path}'}), 404
                
                image = preprocess(Image.open(image_full_path)).unsqueeze(0)
                image_embedding = F.normalize(model.encode_image(image))
                query_embedding = F.normalize(lambda_val * text_embedding + (1.0 - lambda_val) * image_embedding)
            except Exception as e:
                return jsonify({'error': f'Error processing image: {str(e)}'}), 500
 
        # Inside the search route
        # Get similarities      
        embeddings = torch.tensor(df['embedding'].values.tolist())
        similarities = F.cosine_similarity(query_embedding, embeddings)

        # Convert similarities to numpy array, making sure to detach first
        similarities_np = similarities.detach().cpu().numpy()

        # Get top results
        top_k = 5
        top_indices = similarities_np.argsort()[-top_k:][::-1]  # Get last k indices in descending order

        results = []
        for idx in top_indices:
            idx = int(idx)
            results.append({
                'image_path': df.iloc[idx]['file_name'],
                'similarity': float(similarities_np[idx])
            })

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images/<path:filename>')
def serve_image(filename):
    # Try different directories in order
    for directory in [IMAGES_DIR, UPLOAD_FOLDER, DEMO_FOLDER]:
        try:
            return send_from_directory(directory, filename)
        except FileNotFoundError:
            continue
    return 'Image not found', 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'success': True, 'filename': filename})

if __name__ == '__main__':
    app.run(debug=True)