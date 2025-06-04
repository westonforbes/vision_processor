import cv2
class Display:
    
    def __init__(self, thread_flags, frame_queue, processed_queue, console):
            
        # Flags for inter-thread communication.
        self.thread_flags = thread_flags

        # Queue for frames captured from the camera.
        self.frame_queue = frame_queue

        # Queue for processed frames.
        self.processed_queue = processed_queue

        # Console for output messages.
        self.console = console

    def display_frames(self):

        while True:

            # Indicate the display thread is running.
            self.thread_flags['display_running'] = True

            # Get a frame from the processed queue.
            frame = self.processed_queue.get()

            # Show the frame in a window.
            cv2.imshow('camera feed', frame)

            # If the user presses 'q', break the loop.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Release the camera and close the window.
        cv2.destroyAllWindows()

        # Indicate the display thread is no longer running.
        self.thread_flags['display_running'] = False