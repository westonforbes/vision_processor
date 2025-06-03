import cv2
from my_little_snake_helpers.console import Console

class Camera():
    
    
    def __init__(self, camera_index=0, resolution=(480, 270)):

        # Initialize the camera index.
        self.camera_index = camera_index

        # Initialize the console for output.
        self.console = Console()

        # Initialize the camera with DirectShow backend.
        self.capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)

        # 1920 x 1080 is full resolution.
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        
        # Check if the camera opened successfully.
        if not self.capture.isOpened():
            self.console.fancy_print("<BAD>failed to open camera.</BAD>")
            raise RuntimeError("failed to open camera.")


    def open_window(self):

        # Loop indefinately to capture frames.
        while True:

            # Read a frame from the camera.
            return_value, frame = self.capture.read()

            # If the frame was not read successfully, break the loop.
            if not return_value:
                self.console.fancy_print("<BAD>failed to read frame.</BAD>")
                break

            # Display the frame in a window.
            cv2.imshow("Camera", frame)

            # Check to see if the user pressed the 'q' key to quit.
            # If so, break the loop.
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): break

        # Release the camera and close the window.
        self.capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    
    # Create a Camera object with default parameters.
    camera = Camera()

    # Open the camera window to display the video feed.
    camera.open_window()