from flask import Flask, Response, render_template, jsonify, request
import cv2
import time
import threading
import os

# Import our modules
from src.morse_converter import MorseConverter
from src.blink_detector import BlinkDetector
from src.text_predictor import TextPredictor

# Create Flask application
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

# Initialize components with default timing
morse_converter = MorseConverter()
blink_detector = BlinkDetector()
text_predictor = TextPredictor()
# Global variables
camera_active = False
last_frame = None
camera_thread = None

def camera_loop():
    """Background thread for processing camera frames"""
    global camera_active, last_frame
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Starting camera thread...")
    camera_active = True
    
    try:
        while camera_active:
            ret, frame = cap.read()
            if not ret:
                print("Error reading frame")
                break
            
            # Flip frame horizontally for more intuitive experience
            frame = cv2.flip(frame, 1)
            
            # Process frame to detect blinks and update Morse code
            processed_frame = blink_detector.process_frame(frame, morse_converter)
            
            # Encode frame for streaming
            ret, jpeg = cv2.imencode('.jpg', processed_frame)
            if ret:
                last_frame = jpeg.tobytes()
            
            # Small delay to prevent high CPU usage
            time.sleep(0.05)
    finally:
        camera_active = False
        cap.release()
        print("Camera thread stopped")

def start_camera():
    """Start the camera thread if not already running"""
    global camera_thread, camera_active
    
    if camera_thread is None or not camera_thread.is_alive():
        camera_active = True
        camera_thread = threading.Thread(target=camera_loop)
        camera_thread.daemon = True
        camera_thread.start()
        # Give camera time to initialize
        time.sleep(2)

@app.route('/')
def index():
    """Main page route"""
    # Start camera if not already running
    start_camera()
    
    # Render template with current settings
    return render_template('index.html',
                         morse_table=morse_converter.get_morse_table(),
                         decoded_text=morse_converter.decoded_text,
                         dot_max=morse_converter.DOT_MAX,
                         dash_min=morse_converter.DASH_MIN,
                         dash_max=morse_converter.DASH_MAX,
                         char_pause=morse_converter.CHAR_PAUSE,
                         word_pause=morse_converter.WORD_PAUSE)

@app.route('/video_feed')
def video_feed():
    """Route for streaming video"""
    def generate():
        while True:
            if last_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')
            time.sleep(0.1)
    return Response(generate(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_decoded_text')
def get_decoded_text():
    """API endpoint to get the latest decoded text"""
    return morse_converter.decoded_text

@app.route('/camera_status')
def camera_status():
    """API endpoint to check camera status"""
    return jsonify({'active': camera_active})

@app.route('/reset_text', methods=['POST'])
def reset_text():
    """API endpoint to reset the decoded text"""
    morse_converter.decoded_text = ""
    morse_converter.current_code = ""
    return jsonify({'success': True})

@app.route('/update_timing', methods=['POST'])
def update_timing():
    """API endpoint to update timing parameters"""
    data = request.json
    morse_converter.DOT_MAX = float(data.get('dot_max', morse_converter.DOT_MAX))
    morse_converter.DASH_MIN = float(data.get('dash_min', morse_converter.DASH_MIN))
    morse_converter.DASH_MAX = float(data.get('dash_max', morse_converter.DASH_MAX))
    morse_converter.CHAR_PAUSE = float(data.get('char_pause', morse_converter.CHAR_PAUSE))
    morse_converter.WORD_PAUSE = float(data.get('word_pause', morse_converter.WORD_PAUSE))
    return jsonify({'success': True})

@app.route('/start_camera', methods=['POST'])
def start_camera_endpoint():
    """API endpoint to start the camera process"""
    start_camera()
    return jsonify({'success': True})

@app.route('/stop_camera', methods=['POST'])
def stop_camera_endpoint():
    """API endpoint to stop the camera process"""
    global camera_active
    camera_active = False
    return jsonify({'success': True})

@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    text = request.json.get('text', '')
    suggestions = text_predictor.get_suggestions(text)
    return jsonify({'suggestions': suggestions})

if __name__ == '__main__':
    # Create necessary directories if they don't exist
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=8081, threaded=True, debug=True)


@app.route('/predict_word', methods=['POST'])
def predict_word():
    partial_word = request.json.get('partial_word', '')
    if not partial_word:
        return jsonify({'predicted_word': ''})
    
    # Get suggestions from the text predictor
    suggestions = text_predictor.get_suggestions(partial_word)
    
    # If we have suggestions, return the first one as the most likely prediction
    predicted_word = suggestions[0] if suggestions else ''
    
    return jsonify({'predicted_word': predicted_word})

@app.route('/update_decoded_text', methods=['POST'])
def update_decoded_text():
    text = request.json.get('text', '')
    morse_converter.decoded_text = text
    return jsonify({'success': True})
