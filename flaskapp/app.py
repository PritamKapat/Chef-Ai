from flask import Flask, request, render_template, redirect, url_for
import tensorflow as tf
from tensorflow import keras
import os
from werkzeug.utils import secure_filename
import numpy as np
from keras.models import load_model
from keras.preprocessing import image

# Flask setup
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load your CNN model
model = load_model('models/trained_model (1).h5')  # Adjust path if needed

# Define image size (as per your model input)
IMAGE_SIZE = (64, 64)

# Class names from your folders
class_names = [
    'apple', 'banana', 'beetroot', 'bell pepper', 'banana', 'capsicum',
    'carrot', 'cauliflower', 'chilli pepper', 'corn', 'cucumber', 'eggplant',
    'garlic', 'ginger', 'grapes', 'jalepeno', 'kiwi', 'lemon', 'lettuce',
    'mango', 'onion', 'orange', 'paprika', 'pear', 'peas', 'pineapple',
    'pomegranate', 'potato', 'raddish', 'soy beans', 'spinach', 'sweetcorn',
    'sweetpotato', 'tomato', 'turnip', 'watermelon'
]

# Prediction function
def predict_image(file_path):
    img = image.load_img(file_path, target_size=IMAGE_SIZE)
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    return prediction

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Upload + Predict
@app.route('/predict', methods=['POST'])
def upload_and_predict():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        result = predict_image(file_path)
        predicted_class_index = np.argmax(result)
        predicted_label = class_names[predicted_class_index]
        confidence = round(np.max(result) * 100, 2)
        
        return f'Predicted Class: {predicted_label} (Confidence: {confidence}%)'

if __name__ == '__main__':
    app.run(debug=True)
