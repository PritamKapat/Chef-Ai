import tensorflow as tf
import numpy as np
import os
import cv2
from keras.preprocessing import image

# Load the model directly
model_path = os.path.join(os.getcwd(), 'models', 'trained_model (1).h5')
print(f"Loading model from: {model_path}")

try:
    cnn = tf.keras.models.load_model(model_path)
    print("Model loaded successfully!")
    print(f"Model input shape: {cnn.input_shape}")
    print(f"Model output shape: {cnn.output_shape}")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

CLASS_NAMES = [
    'apple', 'banana', 'beetroot', 'bell pepper', 'cabbage', 'capsicum', 'carrot',
    'cauliflower', 'chilli pepper', 'corn', 'cucumber', 'eggplant', 'garlic',
    'ginger', 'grapes', 'jalepeno', 'kiwi', 'lemon', 'lettuce', 'mango', 'onion',
    'orange', 'paprika', 'pear', 'peas', 'pineapple', 'pomegranate', 'potato',
    'raddish', 'soy beans', 'spinach', 'sweetcorn', 'sweetpotato', 'tomato',
    'turnip', 'watermelon'
]

def test_model_with_random_image():
    """Test the model with a random image to see if it's working"""
    print("\n=== Testing with random image ===")
    
    # Create a random image
    random_img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    
    # Convert to array and normalize
    img_array = image.img_to_array(random_img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    
    print(f"Random image shape: {img_array.shape}")
    print(f"Random image min: {np.min(img_array)}, max: {np.max(img_array)}")
    
    # Make prediction
    predictions = cnn.predict(img_array)
    
    print(f"Prediction shape: {predictions.shape}")
    print(f"All predictions: {predictions[0]}")
    
    result_index = np.argmax(predictions)
    predicted_class = CLASS_NAMES[result_index]
    confidence = float(predictions[0][result_index]) * 100
    
    print(f"Predicted class: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")
    
    # Show top 5 predictions
    top_5_indices = np.argsort(predictions[0])[-5:][::-1]
    print("Top 5 predictions:")
    for i, idx in enumerate(top_5_indices):
        print(f"{i+1}. {CLASS_NAMES[idx]}: {predictions[0][idx]*100:.2f}%")

def test_model_with_constant_image():
    """Test the model with a constant image to see if it's stuck"""
    print("\n=== Testing with constant image ===")
    
    # Create a constant image (all zeros)
    constant_img = np.zeros((64, 64, 3), dtype=np.uint8)
    
    # Convert to array and normalize
    img_array = image.img_to_array(constant_img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    
    print(f"Constant image shape: {img_array.shape}")
    print(f"Constant image min: {np.min(img_array)}, max: {np.max(img_array)}")
    
    # Make prediction
    predictions = cnn.predict(img_array)
    
    print(f"Prediction shape: {predictions.shape}")
    print(f"All predictions: {predictions[0]}")
    
    result_index = np.argmax(predictions)
    predicted_class = CLASS_NAMES[result_index]
    confidence = float(predictions[0][result_index]) * 100
    
    print(f"Predicted class: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")
    
    # Show top 5 predictions
    top_5_indices = np.argsort(predictions[0])[-5:][::-1]
    print("Top 5 predictions:")
    for i, idx in enumerate(top_5_indices):
        print(f"{i+1}. {CLASS_NAMES[idx]}: {predictions[0][idx]*100:.2f}%")

def test_model_with_ones_image():
    """Test the model with an all-ones image"""
    print("\n=== Testing with all-ones image ===")
    
    # Create an all-ones image
    ones_img = np.ones((64, 64, 3), dtype=np.uint8) * 255
    
    # Convert to array and normalize
    img_array = image.img_to_array(ones_img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    
    print(f"Ones image shape: {img_array.shape}")
    print(f"Ones image min: {np.min(img_array)}, max: {np.max(img_array)}")
    
    # Make prediction
    predictions = cnn.predict(img_array)
    
    print(f"Prediction shape: {predictions.shape}")
    print(f"All predictions: {predictions[0]}")
    
    result_index = np.argmax(predictions)
    predicted_class = CLASS_NAMES[result_index]
    confidence = float(predictions[0][result_index]) * 100
    
    print(f"Predicted class: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")
    
    # Show top 5 predictions
    top_5_indices = np.argsort(predictions[0])[-5:][::-1]
    print("Top 5 predictions:")
    for i, idx in enumerate(top_5_indices):
        print(f"{i+1}. {CLASS_NAMES[idx]}: {predictions[0][idx]*100:.2f}%")

if __name__ == "__main__":
    print("Testing the image classification model...")
    
    test_model_with_random_image()
    test_model_with_constant_image()
    test_model_with_ones_image()
    
    print("\n=== Test completed ===")
