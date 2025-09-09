"""
Model Retraining Script for Image Classification
This script retrains the model using transfer learning to fix the bias issue.
"""

import tensorflow as tf
from tensorflow.keras.applications import ResNet50V2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import numpy as np
import os
import matplotlib.pyplot as plt

# Configuration
IMG_SIZE = 64
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001
NUM_CLASSES = 36

CLASS_NAMES = [
    'apple', 'banana', 'beetroot', 'bell pepper', 'cabbage', 'capsicum', 'carrot',
    'cauliflower', 'chilli pepper', 'corn', 'cucumber', 'eggplant', 'garlic',
    'ginger', 'grapes', 'jalepeno', 'kiwi', 'lemon', 'lettuce', 'mango', 'onion',
    'orange', 'paprika', 'pear', 'peas', 'pineapple', 'pomegranate', 'potato',
    'raddish', 'soy beans', 'spinach', 'sweetcorn', 'sweetpotato', 'tomato',
    'turnip', 'watermelon'
]

def create_model():
    """
    Create a transfer learning model using ResNet50V2
    """
    # Load pre-trained ResNet50V2 model
    base_model = ResNet50V2(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    
    # Freeze the base model layers
    base_model.trainable = False
    
    # Create the model
    model = tf.keras.Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dropout(0.5),  # Add dropout to prevent overfitting
        Dense(512, activation='relu'),
        Dropout(0.3),
        Dense(256, activation='relu'),
        Dropout(0.2),
        Dense(NUM_CLASSES, activation='softmax')
    ])
    
    # Compile the model
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model, base_model

def create_data_generators(train_dir, val_dir):
    """
    Create data generators with augmentation
    """
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Only rescaling for validation
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Create generators
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    return train_generator, val_generator

def train_model(model, train_generator, val_generator):
    """
    Train the model with callbacks
    """
    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        ),
        ModelCheckpoint(
            'best_model.h5',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]
    
    # Train the model
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    return history

def fine_tune_model(model, base_model, train_generator, val_generator):
    """
    Fine-tune the model by unfreezing some layers
    """
    # Unfreeze the top layers of the base model
    base_model.trainable = True
    
    # Freeze the bottom layers
    for layer in base_model.layers[:-30]:
        layer.trainable = False
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE/10),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Fine-tune for a few more epochs
    fine_tune_history = model.fit(
        train_generator,
        epochs=20,
        validation_data=val_generator,
        callbacks=[
            EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-8)
        ],
        verbose=1
    )
    
    return fine_tune_history

def plot_training_history(history, fine_tune_history=None):
    """
    Plot training history
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot accuracy
    axes[0, 0].plot(history.history['accuracy'], label='Training Accuracy')
    axes[0, 0].plot(history.history['val_accuracy'], label='Validation Accuracy')
    if fine_tune_history:
        axes[0, 0].plot(range(len(history.history['accuracy']), 
                             len(history.history['accuracy']) + len(fine_tune_history.history['accuracy'])),
                       fine_tune_history.history['accuracy'], label='Fine-tune Training Accuracy')
        axes[0, 0].plot(range(len(history.history['val_accuracy']), 
                             len(history.history['val_accuracy']) + len(fine_tune_history.history['val_accuracy'])),
                       fine_tune_history.history['val_accuracy'], label='Fine-tune Validation Accuracy')
    axes[0, 0].set_title('Model Accuracy')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].legend()
    
    # Plot loss
    axes[0, 1].plot(history.history['loss'], label='Training Loss')
    axes[0, 1].plot(history.history['val_loss'], label='Validation Loss')
    if fine_tune_history:
        axes[0, 1].plot(range(len(history.history['loss']), 
                             len(history.history['loss']) + len(fine_tune_history.history['loss'])),
                       fine_tune_history.history['loss'], label='Fine-tune Training Loss')
        axes[0, 1].plot(range(len(history.history['val_loss']), 
                             len(history.history['val_loss']) + len(fine_tune_history.history['val_loss'])),
                       fine_tune_history.history['val_loss'], label='Fine-tune Validation Loss')
    axes[0, 1].set_title('Model Loss')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    
    plt.tight_layout()
    plt.savefig('training_history.png')
    plt.show()

def evaluate_model(model, val_generator):
    """
    Evaluate the model and print detailed metrics
    """
    # Evaluate the model
    evaluation = model.evaluate(val_generator, verbose=1)
    print(f"\nTest Loss: {evaluation[0]:.4f}")
    print(f"Test Accuracy: {evaluation[1]:.4f}")
    
    # Get predictions
    predictions = model.predict(val_generator, verbose=1)
    y_true = val_generator.classes
    
    # Calculate per-class accuracy
    from sklearn.metrics import classification_report, confusion_matrix
    import seaborn as sns
    
    y_pred = np.argmax(predictions, axis=1)
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=CLASS_NAMES))
    
    # Plot confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(20, 20))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    plt.show()

def main():
    """
    Main training function
    """
    print("Starting model retraining...")
    
    # Check if data directories exist
    train_dir = "dataset/train"  # Update this path
    val_dir = "dataset/val"      # Update this path
    
    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        print(f"Error: Data directories not found!")
        print(f"Expected: {train_dir} and {val_dir}")
        print("Please organize your dataset in the following structure:")
        print("dataset/")
        print("├── train/")
        print("│   ├── apple/")
        print("│   ├── banana/")
        print("│   └── ...")
        print("└── val/")
        print("    ├── apple/")
        print("    ├── banana/")
        print("    └── ...")
        return
    
    # Create model
    print("Creating model...")
    model, base_model = create_model()
    model.summary()
    
    # Create data generators
    print("Creating data generators...")
    train_generator, val_generator = create_data_generators(train_dir, val_dir)
    
    print(f"Number of training samples: {train_generator.samples}")
    print(f"Number of validation samples: {val_generator.samples}")
    print(f"Number of classes: {len(train_generator.class_indices)}")
    
    # Train the model
    print("Training model...")
    history = train_model(model, train_generator, val_generator)
    
    # Fine-tune the model
    print("Fine-tuning model...")
    fine_tune_history = fine_tune_model(model, base_model, train_generator, val_generator)
    
    # Plot training history
    print("Plotting training history...")
    plot_training_history(history, fine_tune_history)
    
    # Evaluate the model
    print("Evaluating model...")
    evaluate_model(model, val_generator)
    
    # Save the final model
    print("Saving model...")
    model.save('retrained_model.h5')
    print("Model saved as 'retrained_model.h5'")
    
    print("Training completed!")

if __name__ == "__main__":
    main()

