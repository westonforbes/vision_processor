import cv2
import queue
class Capture:
    
    def __init__(self, thread_flags, frame_queue, processed_queue, console):
            
        # Flags for inter-thread communication.
        self.thread_flags = thread_flags

        # Queue for frames captured from the camera.
        self.frame_queue = frame_queue

        # Queue for processed frames.
        self.processed_queue = processed_queue

        # Console for output messages.
        self.console = console

    def capture_frames(self):

        # Initialize video capture from the default camera using DirectShow.
        # cap = cv2.VideoCapture(0) # Default backend
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Using DirectShow for potentially better compatibility/performance on Windows.
        
        while True:
            
            # Indicate the capture thread is running.
            self.thread_flags['capture_running'] = True

            # Read a frame from the camera.
            ret, frame = cap.read()
            
            # If a frame was not successfully read (e.g., camera disconnected), break the loop.
            if not ret:
                self.console.fancy_print("<WARN>failed to capture frame. exiting capture thread.</WARN>")
                break
                
            # Put the captured frame into the queue for processing.
            # If the queue is full, this will block until a slot is available.
            try:
                self.frame_queue.put(frame, timeout=1)
            except queue.Full:
                self.frame_queue.get()  # Remove the oldest frame to make space for the new one.


        # Release the camera resource when the loop ends.
        cap.release()
        
        # Indicate the capture thread is no longer running.
        self.thread_flags['capture_running'] = False
        self.console.fancy_print("<INFO>capture thread stopped.</INFO>")

