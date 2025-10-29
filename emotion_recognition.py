import cv2
import numpy as np
import tensorflow as tf

# Load the pre-trained emotion detection model
print("Loading model...")
model = tf.keras.models.load_model('EM.h5')
print("Model loaded successfully!")

# Define emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# Load Haar Cascade for face detection
print("Loading face cascade classifier...")
face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)
print("Face cascade classifier loaded successfully!")

# Function to preprocess the image for emotion detection
def preprocess_image(img):
    # Resize image to 64x64 as expected by the model
    img = cv2.resize(img, (64, 64))
    # Convert to float32 and normalize
    img = img.astype('float32') / 255.0
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    return img

# Function to detect emotion in a face
def detect_emotion(face_img):
    # Preprocess the image
    processed_img = preprocess_image(face_img)
    # Predict emotion
    predictions = model.predict(processed_img, verbose=0)
    # Get the emotion with highest probability
    emotion_idx = np.argmax(predictions)
    emotion_confidence = np.max(predictions)
    return emotion_labels[emotion_idx], emotion_confidence

# Main function to run real-time emotion detection
def run_emotion_detection():
    # Open webcam
    print("Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Emotion Recognition System Started")
    print("Press 'q' to quit")
    
    while True:
        # Read frame from webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from webcam")
            break
            
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
        
        # Display the frame
        cv2.imshow('Emotion Recognition', frame)
        
        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_emotion_detection()