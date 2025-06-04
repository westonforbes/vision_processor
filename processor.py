import cv2
import queue


class Processor:
    
    def __init__(self, thread_flags, processor_flags, frame_queue, processed_queue, console):
        
        # Flags for inter-thread communication.
        self.thread_flags = thread_flags

        # Flags for video processing options.
        self.processor_flags = processor_flags

        # Queue for frames captured from the camera.
        self.frame_queue = frame_queue

        # Queue for processed frames.
        self.processed_queue = processed_queue

        # Console for output messages.
        self.console = console

        self.previous_frame = None  # Initialize the previous frame variable.

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
            frame = self.convert_to_black_and_white(frame)
            frame = self.binary_difference_threshold(frame)
                
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
