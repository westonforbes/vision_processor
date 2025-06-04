import cv2
import queue


class Processor:
    
    def __init__(self, thread_flags, frame_queue, processed_queue, console):
        
        # Initialize global variables to track the state of the processing thread.
        self.thread_flags = thread_flags

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


            # If video processing is enabled, process the frame.
            if not self.thread_flags['no_video_processing']:
                frame = self.video_processing(frame)
                
            # Put the (potentially processed) frame into the processed queue.
            # If the queue is full, this will block until a slot is available.
            try:
                self.processed_queue.put(frame, timeout=1) # Add a timeout
            except queue.Full:
                self.console.fancy_print("<WARN>Processed queue is full. Dropping frame.</WARN>")
                # If the processed queue is full, we might want to clear the input queue
                # to process more recent frames, or just drop the current one.
                # For now, just dropping.
                continue
        
        # Indicate the processing thread is no longer running.
        self.thread_flags['processing_running'] = False
        self.console.fancy_print("<INFO>Processing thread stopped.</INFO>")

    def video_processing(self, frame):

        # Flip the frame horizontally and convert it to grayscale.
        flipped_frame = cv2.flip(frame, 1)
        gray_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2GRAY)

        # If this is the first frame, do no further processing.
        if self.previous_frame is None:
            self.previous_frame = gray_frame.copy()
            return gray_frame
        
        # Compute the absolute difference between current frame and previous frame.
        diff = cv2.absdiff(self.previous_frame, gray_frame)

        # Threshold the difference to get motion areas.
        _, threshold_frame = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        # Dilate to fill in holes.
        #threshold_frame = cv2.dilate(thresh, None, iterations=2)

        # Update the previous frame.
        self.previous_frame = gray_frame.copy()

        return threshold_frame