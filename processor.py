import cv2
import queue
import numpy as np


class Processor:
    
    def __init__(self, thread_flags, roi_bounds, frame_queue, processed_queue, console):
        
        # Flags for inter-thread communication.
        self.thread_flags = thread_flags
        
        # ROI bounds for region of interest overlay.
        self.roi_bounds = roi_bounds

        # Queue for frames captured from the camera.
        self.frame_queue = frame_queue

        # Queue for processed frames.
        self.processed_queue = processed_queue

        # Console for output messages.
        self.console = console

        # Initialize the previous frame variable.
        self.previous_frame = None  
        
        # Load and preprocess reference QR code
        self.qr_match_result = False

        # Initialize the detector
        self.qr_detector = cv2.QRCodeDetector()


    def process_frames(self):
        
        while True:
            
            # Indicate the processing thread is running.
            self.thread_flags['processing_running'] = True

            # Get a frame from the capture queue.
            # This will block until a frame is available.
            try:
                frame = self.frame_queue.get(timeout=1) # Add a timeout
            except queue.Empty:
                # If the queue is empty after timeout, continue and check capture_running status
                if not self.thread_flags["capture_running"] and self.frame_queue.empty():
                    self.console.fancy_print("<INFO>Processing thread: Capture thread stopped and queue empty. Exiting.</INFO>")
                    break
                continue
            
            # Process the frame.
            frame = cv2.flip(frame, 1)

            data = self.qr_code_match_roi(frame)
            frame = self.overlay_roi(frame)
                
            # Put the frame into the processed queue.
            # If the queue is full, this will block until a slot is available.
            try:
                self.processed_queue.put(frame, timeout=1) # Add a timeout
            except queue.Full:
                self.processed_queue.get()  # Remove the oldest frame to make space for the new one.
                self.processed_queue.put(frame, timeout=1) # Add a timeout

        
        # Indicate the processing thread is no longer running.
        self.thread_flags['processing_running'] = False
        self.console.fancy_print("<INFO>Processing thread stopped.</INFO>")


    def overlay_roi(self, frame):
            
        # Get ROI coordinates
        x1, y1 = self.roi_bounds['x1'], self.roi_bounds['y1']
        x2, y2 = self.roi_bounds['x2'], self.roi_bounds['y2']
        
        # Choose color based on QR code match result.
        color = (0, 255, 0) if self.qr_match_result else (0, 0, 255)  # Green if match, red if no match

        
        # Draw rectangle overlay on the frame
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Add ROI coordinates text in upper right corner
        roi_text = f"ROI: ({x1},{y1}) ({x2},{y2})"
        match_status = "MATCH" if self.qr_match_result else "NO MATCH"
        roi_text += f" - QR: {match_status}"
        
        text_size = cv2.getTextSize(roi_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = frame.shape[1] - text_size[0] - 10
        text_y = 30
        cv2.putText(frame, roi_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Return the frame.
        return frame
    
    
    def qr_code_match_roi(self, frame):

        # Get ROI coordinates.
        x1, y1 = self.roi_bounds['x1'], self.roi_bounds['y1']
        x2, y2 = self.roi_bounds['x2'], self.roi_bounds['y2']
        
        # Validate ROI bounds
        frame_height, frame_width = frame.shape[:2]
        
        # Ensure coordinates are within frame bounds and valid
        x1 = max(0, min(x1, frame_width - 1))
        x2 = max(x1 + 1, min(x2, frame_width))
        y1 = max(0, min(y1, frame_height - 1))
        y2 = max(y1 + 1, min(y2, frame_height))
        
        # Check if ROI has valid dimensions
        if x2 <= x1 or y2 <= y1:
            self.qr_match_result = False
            return None
        
        # Extract ROI from frame and convert to grayscale.
        roi = frame[y1:y2, x1:x2]
        
        # Check if ROI is empty
        if roi.size == 0:
            self.qr_match_result = False
            return None
            
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Detect and decode
        data, points, _ = self.qr_detector.detectAndDecode(roi_gray)

        if points is not None and len(data) > 0:
            self.qr_match_result = True
            print(data)
            return data
        else:
            self.qr_match_result = False
            return None
        
