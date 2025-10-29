import os
import cv2
import numpy as np
import tensorflow as tf

# Using tf.keras.models.load_model directly to avoid static analysis warnings
load_model = tf.keras.models.load_model

# Flask imports - importing directly to avoid static analysis warnings
from flask import Flask, render_template, Response, jsonify, request

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Load the pre-trained emotion detection model
print("Loading emotion detection model...")
model = load_model('EM.h5')
print("Model loaded successfully!")

# Define emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# Global variable for camera
camera = None

def get_face_cascade():
    """Get face cascade classifier with fallback handling"""
    try:
        # Try to use cv2.data.haarcascades
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        return cv2.CascadeClassifier(cascade_path)
    except (AttributeError, TypeError):
        # Fallback to direct path
        try:
            cascade_path = 'haarcascade_frontalface_default.xml'
            if not os.path.exists(cascade_path):
                # Try OpenCV's default data path
                import sys
                opencv_data_path = os.path.join(sys.prefix, 'share', 'opencv4', 'haarcascades')
                cascade_path = os.path.join(opencv_data_path, 'haarcascade_frontalface_default.xml')
            return cv2.CascadeClassifier(cascade_path)
        except:
            # Last resort - try with just the filename
            return cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def preprocess_image(img):
    """Preprocess image for emotion detection"""
    # Ensure the image is the right size and type
    if img is None:
        raise ValueError("Input image is None")
    
    # Resize image to 64x64 as expected by the model
    img = cv2.resize(img, (64, 64))
    # Convert to float32 and normalize to [0, 1] range
    img = img.astype('float32') / 255.0
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    return img

def detect_emotion(face_img):
    """Detect emotion in a face image with improved validation"""
    # Validate input
    if face_img is None:
        raise ValueError("Input face image is None")
    
    # Preprocess the image
    processed_img = preprocess_image(face_img)
    
    # Validate processed image shape
    if processed_img.shape != (1, 64, 64, 3):
        raise ValueError(f"Invalid processed image shape: {processed_img.shape}")
    
    # Predict emotion
    predictions = model.predict(processed_img, verbose=0)
    
    # Validate predictions
    if predictions.shape != (1, 7):
        raise ValueError(f"Invalid predictions shape: {predictions.shape}")
    
    # Get the emotion with highest probability
    emotion_idx = np.argmax(predictions)
    emotion_confidence = np.max(predictions)
    
    # Validate emotion index
    if emotion_idx < 0 or emotion_idx >= len(emotion_labels):
        raise ValueError(f"Invalid emotion index: {emotion_idx}")
    
    return emotion_labels[emotion_idx], emotion_confidence

def generate_frames():
    """Generate frames from webcam for streaming"""
    global camera
    # Initialize camera
    camera = cv2.VideoCapture(0)
    
    # Load Haar Cascade for face detection
    face_cascade = get_face_cascade()
    
    while True:
        # Read frame from webcam
        success, frame = camera.read()
        if not success:
            break
        else:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Process each detected face
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Extract face region
                face_roi = frame[y:y+h, x:x+w]
                
                # Detect emotion
                emotion, confidence = detect_emotion(face_roi)
                
                # Display emotion and confidence
                text = f'{emotion} ({confidence:.2f})'
                cv2.putText(frame, text, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            # Yield frame in required format for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Render the main page"""
    return render_template('ultimate.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload')
def upload_page():
    """Render the upload page"""
    return render_template('ultimate.html')

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion_upload():
    """Detect emotion in uploaded image"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if file:
        # Read image file
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Check if image was decoded successfully
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Load Haar Cascade for face detection
        face_cascade = get_face_cascade()
        
        # Convert to grayscale
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except cv2.error:
            return jsonify({'error': 'Error processing image'}), 400
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return jsonify({'error': 'No face detected in the image'}), 400
        
        # Process all detected faces
        results = []
        for (x, y, w, h) in faces:
            # Extract face region with bounds checking
            if y+h <= img.shape[0] and x+w <= img.shape[1]:
                face_roi = img[y:y+h, x:x+w]
                
                try:
                    # Detect emotion
                    emotion, confidence = detect_emotion(face_roi)
                    
                    # Get all predictions
                    processed_img = preprocess_image(face_roi)
                    predictions = model.predict(processed_img, verbose=0)[0]
                    
                    # Create response with all emotion probabilities
                    emotion_probabilities = {}
                    for i, label in enumerate(emotion_labels):
                        emotion_probabilities[label] = float(predictions[i])
                    
                    results.append({
                        'emotion': emotion,
                        'confidence': float(confidence),
                        'emotion_probabilities': emotion_probabilities,
                        'bbox': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)}
                    })
                except Exception as e:
                    # Log error and continue with other faces
                    print(f"Error processing face at ({x}, {y}): {str(e)}")
                    continue
        
        # Return results for all faces
        return jsonify({
            'faces_detected': len(faces),
            'results': results
        })

@app.route('/stop_camera')
def stop_camera():
    """Stop the camera"""
    global camera
    if camera is not None:
        camera.release()
        camera = None
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Get debug mode from environment variable or default to False
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)