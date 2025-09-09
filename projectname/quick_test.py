"""
Quick test script to verify the image classification fixes
"""

import tensorflow as tf
import numpy as np
import cv2
import os
from keras.preprocessing import image

# Load the model
model_path = os.path.join(os.getcwd(), 'models', 'trained_model (1).h5')
print(f"Loading model from: {model_path}")

try:
    cnn = tf.keras.models.load_model(model_path)
    print("Model loaded successfully!")
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

def test_image_classification(image_path):
    """
    Test image classification with the fixed preprocessing
    """
    print(f"\n=== Testing: {image_path} ===")
    
    # Read and preprocess image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not read image: {image_path}")
        return
    
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize to match model input
    img = cv2.resize(img, (64, 64))
    
    # Apply enhanced preprocessing (same as in views.py)
    img = img.astype(np.float32) / 255.0
    
    # Add small random noise to reduce bias
    noise = np.random.normal(0, 0.01, img.shape)
    img = np.clip(img + noise, 0, 1)
    
    # Convert to array and add batch dimension
    img_array = np.expand_dims(img, axis=0)
    
    print(f"Image shape: {img_array.shape}")
    print(f"Image min: {np.min(img_array):.4f}, max: {np.max(img_array):.4f}")
    
    # Make prediction
    predictions = cnn.predict(img_array, verbose=0)
    
    # Get top 5 predictions
    top_5_indices = np.argsort(predictions[0])[-5:][::-1]
    result_index = top_5_indices[0]
    predicted_class = CLASS_NAMES[result_index]
    confidence = float(predictions[0][result_index]) * 100
    
    # Check for low confidence
    if confidence < 20:
        predicted_class = "Unknown/Uncertain"
        confidence = 0
    
    print(f"Predicted class: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")
    
    # Check for cabbage bias
    cabbage_index = CLASS_NAMES.index('cabbage')
    cabbage_rank = np.where(top_5_indices == cabbage_index)[0]
    if len(cabbage_rank) > 0 and cabbage_rank[0] <= 2:
        print("⚠️  WARNING: Model shows bias towards cabbage")
    
    print("Top 5 predictions:")
    for i, idx in enumerate(top_5_indices):
        print(f"  {i+1}. {CLASS_NAMES[idx]}: {predictions[0][idx]*100:.2f}%")
    
    return predicted_class, confidence, len(cabbage_rank) > 0 and cabbage_rank[0] <= 2

def main():
    """
    Test with sample images
    """
    print("Testing image classification with fixes...")
    
    # Test with sample images if they exist
    test_images = [
        "media/temp/Image_1.jpg",
        "media/temp/Image_5.jpg"
    ]
    
    results = []
    
    for image_path in test_images:
        if os.path.exists(image_path):
            result = test_image_classification(image_path)
            if result:
                results.append((image_path, *result))
        else:
            print(f"Image not found: {image_path}")
    
    # Summary
    print("\n=== SUMMARY ===")
    if results:
        print(f"Tested {len(results)} images:")
        for image_path, predicted_class, confidence, has_bias in results:
            bias_status = "⚠️  BIAS DETECTED" if has_bias else "✅ No bias"
            print(f"  {image_path}: {predicted_class} ({confidence:.1f}%) - {bias_status}")
    else:
        print("No test images found. Please add some images to test with.")
    
    print("\nTo test with your own images:")
    print("1. Upload images through the web interface at /predict/")
    print("2. Check the console output for debug information")
    print("3. Look for bias warnings in the results")

if __name__ == "__main__":
    main()

