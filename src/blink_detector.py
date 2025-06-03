import cv2
import numpy as np
import time

class BlinkDetector:
    """
    Detects eye blinks using OpenCV Haar cascades with improved reliability
    """
    def __init__(self):
        # Initialize face and eye detectors
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # State tracking for blinks
        self.eyes_closed = False
        self.blink_start = 0
        self.last_blink_end = 0
        
        # Eye state history for more reliable detection
        self.eye_state_history = []
        self.eye_state_buffer_size = 5
        
        # Visual feedback
        self.blink_type = None
        self.blink_display_time = 0
        self.display_duration = 0.5
    
    def detect_eyes(self, frame):
        """
        Detect if eyes are open or closed with improved reliability
        Returns: (is_closed, processed_frame)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
        
        if len(faces) == 0:
            return False, frame
        
        # Get largest face
        face = max(faces, key=lambda x: x[2]*x[3])
        x, y, w, h = face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Detect eyes in face region
        face_roi = gray[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 5)
        
        # If no eyes found, check upper half of face
        if len(eyes) == 0:
            upper_face = face_roi[0:h//2, :]
            eyes = self.eye_cascade.detectMultiScale(upper_face, 1.1, 5)
        
        # Add to history buffer
        eyes_closed = len(eyes) < 2
        self.eye_state_history.append(eyes_closed)
        if len(self.eye_state_history) > self.eye_state_buffer_size:
            self.eye_state_history.pop(0)
        
        # Use majority vote from history for more stable detection
        eyes_closed_stable = sum(self.eye_state_history) > len(self.eye_state_history) // 2
        
        # Draw eye rectangles
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame[y:y+h, x:x+w], (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
        
        return eyes_closed_stable, frame
    
    def process_frame(self, frame, converter):
        """
        Process a video frame to detect blinks and update Morse code
        Returns: processed frame with visual indicators
        """
        frame_out = frame.copy()
        current_time = time.time()
        
        # Detect eye state
        is_closed, frame = self.detect_eyes(frame)
        
        # Blink started (eyes just closed)
        if is_closed and not self.eyes_closed:
            self.eyes_closed = True
            self.blink_start = current_time
            
        # Blink ended (eyes just opened)
        elif not is_closed and self.eyes_closed:
            self.eyes_closed = False
            duration = current_time - self.blink_start
            self.last_blink_end = current_time
            
            # Determine if dot or dash and notify converter
            if duration <= converter.DOT_MAX:
                converter.add_signal(".")
                self.blink_type = "dot"
                print(f"Dot detected ({duration:.2f}s)")
            elif converter.DASH_MIN <= duration <= converter.DASH_MAX:
                converter.add_signal("-")
                self.blink_type = "dash"
                print(f"Dash detected ({duration:.2f}s)")
            
            self.blink_display_time = current_time
        
        # Show blink feedback
        if self.blink_type and (current_time - self.blink_display_time < self.display_duration):
            h, w = frame_out.shape[:2]
            center = (w//2, h//2)
            
            if self.blink_type == "dot":
                cv2.circle(frame_out, center, 50, (0, 255, 0), -1)
                cv2.putText(frame_out, "DOT", (center[0]-35, center[1]+10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            else:
                cv2.rectangle(frame_out, (center[0]-100, center[1]-30), 
                             (center[0]+100, center[1]+30), (0, 0, 255), -1)
                cv2.putText(frame_out, "DASH", (center[0]-45, center[1]+10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        else:
            self.blink_type = None
        
        # Process signals in converter based on time elapsed
        converter.process_timing(current_time, self.last_blink_end)
        
        # Display info
        cv2.putText(frame_out, f"Current: {converter.current_code}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame_out, f"Decoded: {converter.decoded_text[-20:]}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show timing progress
        if converter.current_code:
            time_since_blink = current_time - self.last_blink_end
            progress = min(time_since_blink / converter.CHAR_PAUSE, 1.0)
            bar_w = int(frame_out.shape[1] * 0.7)
            bar_h = 20
            bar_x = (frame_out.shape[1] - bar_w) // 2
            bar_y = frame_out.shape[0] - 50
            
            cv2.rectangle(frame_out, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (100, 100, 100), -1)
            cv2.rectangle(frame_out, (bar_x, bar_y), (bar_x+int(bar_w*progress), bar_y+bar_h), (0, 255, 0), -1)
            cv2.putText(frame_out, "Character progress", (bar_x, bar_y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame_out