from flask import Flask, request, jsonify
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import base64

app = Flask(__name__)

# Load the pre-trained emotion detection model
model = load_model('D:\semester 5\\trials_and_ tests\group-video-chat\emotion_detection_model.h5')
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

@app.route('/process_frame', methods=['POST'])
def process_frame():
    data = request.json
    image_data = data['image'].split(",")[1]
    image = np.frombuffer(base64.b64decode(image_data), dtype=np.uint8)
    frame = cv2.imdecode(image, flags=cv2.IMREAD_COLOR)
    
    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Use OpenCV to detect faces in the frame
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        roi_gray = gray_frame[y:y+h, x:x+w]
        roi_gray = cv2.resize(roi_gray, (48, 48))  # Resize to 48x48 pixels as required by the model

        # Preprocess the ROI
        roi = roi_gray.astype('float') / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        # Make a prediction on the ROI and get the emotion label with the highest probability
        preds = model.predict(roi)[0]
        label = emotion_labels[np.argmax(preds)]

        # Draw a rectangle around the face and the predicted emotion label
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Encode the frame back to base64
    _, buffer = cv2.imencode('.jpg', frame)
    processed_frame = base64.b64encode(buffer).decode('utf-8')
    return jsonify({'image': 'data:image/jpeg;base64,' + processed_frame})

if __name__ == '__main__':
    app.run(debug=True)
