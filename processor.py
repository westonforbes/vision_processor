import cv2
import queue


class Processor:
    
    def __init__(self, thread_flags, processor_flags, roi_bounds, frame_queue, processed_queue, console):
        
        # Flags for inter-thread communication.
        self.thread_flags = thread_flags

        # Flags for video processing options.
        self.processor_flags = processor_flags
        
        # ROI bounds for region of interest overlay.
        self.roi_bounds = roi_bounds

        # Queue for frames captured from the camera.
        self.frame_queue = frame_queue

        # Queue for processed frames.
        self.processed_queue = processed_queue

        # Console for output messages.
        self.console = console

        self.previous_frame = None  # Initialize the previous frame variable.
        
        # Initialize MOG2 background subtractor
        self.mog2 = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

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
            frame = self.flip_horizontally(frame)
            frame = self.gaussian_blur(frame)
            frame = self.convert_to_black_and_white(frame)
            frame = self.binary_difference_threshold(frame)
            frame = self.mog2_motion_detection_roi(frame)
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

    def flip_horizontally(self, frame):
        
        # If the flag is set...
        if self.processor_flags['flip_horizontally']:
            
            # Flip the frame horizontally.
            frame = cv2.flip(frame, 1)
        
        # Return the (possibly flipped) frame.
        return frame

    def convert_to_black_and_white(self, frame):
        
        # If the flag is set...
        if self.processor_flags['black_and_white']:
            
            # Convert the frame to black and white.
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Return the (possibly converted) frame.
        return frame
    
    def gaussian_blur(self, frame):
        
        # If the flag is set...
        if self.processor_flags['gaussian_blur']:
            
            # Add Gaussian blur to the frame.
            frame = cv2.GaussianBlur(frame, (5, 5), 0)
        
        # Return the (possibly converted) frame.
        return frame

    def binary_difference_threshold(self, frame):
        
        if self.processor_flags['motion_detect']:
            

            if self.previous_frame is None:
                self.previous_frame = frame.copy()
                return frame

            if frame.shape != self.previous_frame.shape:
                self.previous_frame = frame.copy()
                return frame

            # Compute the absolute difference
            diff = cv2.absdiff(self.previous_frame, frame)

            # Threshold and dilate
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            thresh = cv2.dilate(thresh, None, iterations=2)

            # Update the previous frame
            self.previous_frame = frame.copy()

            return thresh

        # Update previous_frame for grayscale if needed
        if self.processor_flags['black_and_white']:
            self.previous_frame = frame.copy()

        return frame
    
    def overlay_roi(self, frame):
        
        # If the flag is set...
        if self.processor_flags['roi_enabled']:
            
            # Get ROI coordinates
            x1, y1 = self.roi_bounds['x1'], self.roi_bounds['y1']
            x2, y2 = self.roi_bounds['x2'], self.roi_bounds['y2']
            
            # Draw rectangle overlay on the frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add ROI coordinates text in upper right corner
            roi_text = f"ROI: ({x1},{y1}) ({x2},{y2})"
            text_size = cv2.getTextSize(roi_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            text_x = frame.shape[1] - text_size[0] - 10
            text_y = 30
            cv2.putText(frame, roi_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Return the (possibly overlaid) frame.
        return frame
    
    def mog2_motion_detection_roi(self, frame):
        """
        Apply MOG2 background subtraction within ROI, detect contours, 
        and draw bounding rectangles around detected movement.
        """
        if not self.processor_flags.get('mog2_motion_detect', False):
            return frame
            
        # Get ROI coordinates
        x1, y1 = self.roi_bounds['x1'], self.roi_bounds['y1']
        x2, y2 = self.roi_bounds['x2'], self.roi_bounds['y2']
        
        # Extract ROI from frame
        roi = frame[y1:y2, x1:x2]
        
        # Apply MOG2 background subtraction to ROI
        fg_mask = self.mog2.apply(roi)
        
        # Clean up the mask with morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours in the foreground mask
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and draw bounding rectangles
        min_area = 500  # Minimum contour area to consider
        for contour in contours:
            if cv2.contourArea(contour) > min_area:
                # Get bounding rectangle in ROI coordinates
                x, y, w, h = cv2.boundingRect(contour)
                
                # Convert to frame coordinates by adding ROI offset
                rect_x1 = x1 + x
                rect_y1 = y1 + y
                rect_x2 = x1 + x + w
                rect_y2 = y1 + y + h
                
                # Draw bounding rectangle on the original frame
                cv2.rectangle(frame, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 255), 2)
                
                # Add area text
                area_text = f"Area: {int(cv2.contourArea(contour))}"
                cv2.putText(frame, area_text, (rect_x1, rect_y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        return frame
