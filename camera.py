import cv2
import threading
import queue
from my_little_snake_helpers.console import Console

# Global variables.
frame_queue = queue.Queue(maxsize=10)
processed_queue = queue.Queue(maxsize=10)
previous_frame = None

# Inter-thread flags.
capture_running = False
processing_running = False
display_running = False
no_video_processing = True

# Initialize the console for output.
console = Console()

def capture_frames():

    # Access global variables to indicate that the capture thread is running and for the frame queue.
    global capture_running, frame_queue
    
    # Initialize video capture from the default camera using DirectShow.
    # cap = cv2.VideoCapture(0) # Default backend
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Using DirectShow for potentially better compatibility/performance on Windows.
    
    while True:
        
        # Indicate the capture thread is running.
        capture_running = True

        # Read a frame from the camera.
        ret, frame = cap.read()
        
        # If a frame was not successfully read (e.g., camera disconnected), break the loop.
        if not ret:
            console.fancy_print("<WARN>failed to capture frame. exiting capture thread.</WARN>")
            break
            
        # Put the captured frame into the queue for processing.
        # If the queue is full, this will block until a slot is available.
        try:
            frame_queue.put(frame, timeout=1)
        except queue.Full:
            console.fancy_print("<WARN>frame queue is full. dropping frame.</WARN>")
            continue

    # Release the camera resource when the loop ends.
    cap.release()
    
    # Indicate the capture thread is no longer running.
    capture_running = False
    console.fancy_print("<INFO>capture thread stopped.</INFO>")


def process_frames():

    # Access global variables to indicate that the processing thread is running, 
    # for the frame queues, and to check if video processing is enabled.
    global processing_running, frame_queue, processed_queue, no_video_processing
    
    while True:
        
        # Indicate the processing thread is running.
        processing_running = True

        # Get a frame from the capture queue.
        # This will block until a frame is available.
        try:
            frame = frame_queue.get(timeout=1) # Add a timeout
        except queue.Empty:
            # If the queue is empty after timeout, continue and check capture_running status
            if not capture_running and frame_queue.empty():
                console.fancy_print("<INFO>Processing thread: Capture thread stopped and queue empty. Exiting.</INFO>")
                break
            continue


        # If video processing is enabled, process the frame.
        if not no_video_processing:
            frame = video_processing(frame)
            
        # Put the (potentially processed) frame into the processed queue.
        # If the queue is full, this will block until a slot is available.
        try:
            processed_queue.put(frame, timeout=1) # Add a timeout
        except queue.Full:
            console.fancy_print("<WARN>Processed queue is full. Dropping frame.</WARN>")
            # If the processed queue is full, we might want to clear the input queue
            # to process more recent frames, or just drop the current one.
            # For now, just dropping.
            continue
    
    # Indicate the processing thread is no longer running.
    processing_running = False
    console.fancy_print("<INFO>Processing thread stopped.</INFO>")


def video_processing(frame):

    # Access the global variable to store the previous frame.
    global previous_frame
    
    # Flip the frame horizontally and convert it to grayscale.
    flipped_frame = cv2.flip(frame, 1)
    gray_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2GRAY)

    # If this is the first frame, do no further processing.
    if previous_frame is None:
        previous_frame = gray_frame.copy()
        return gray_frame
    
    # Compute the absolute difference between current frame and previous frame.
    diff = cv2.absdiff(previous_frame, gray_frame)

    # Threshold the difference to get motion areas.
    _, threshold_frame = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

    # Dilate to fill in holes.
    #threshold_frame = cv2.dilate(thresh, None, iterations=2)

    # Update the previous frame.
    previous_frame = gray_frame.copy()

    return threshold_frame
    

def display_frames():

    # Access the global variable to indicate that the display thread is running.
    global display_running
    
    while True:

        # Indicate the display thread is running.
        display_running = True

        # Get a frame from the processed queue.
        frame = processed_queue.get()

        # Show the frame in a window.
        cv2.imshow('camera feed', frame)

        # If the user presses 'q', break the loop.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the camera and close the window.
    cv2.destroyAllWindows()

    # Indicate the display thread is no longer running.
    display_running = False


def start_threads():
    # Access global variables to control thread startup and for console output.
    global capture_running, processing_running, display_running, console
    
    # Clear the console for a cleaner output.
    console.clear()
    
    # Start the capture thread if it's not already running.
    if not capture_running:
        console.fancy_print("<INFO>Starting capture thread...</INFO>")
        threading.Thread(target=capture_frames, daemon=True).start()
        
        # Wait until the capture thread sets its running flag.
        while not capture_running:
            pass
        console.fancy_print("<GOOD>Capture thread started.</GOOD>")

    # Start the processing thread if it's not already running.
    if not processing_running:
        console.fancy_print("<INFO>Starting processing thread...</INFO>")
        threading.Thread(target=process_frames, daemon=True).start()
        
        # Wait until the processing thread sets its running flag.
        while not processing_running:
            pass
        console.fancy_print("<GOOD>Processing thread started.</GOOD>")

    # Start the display thread if it's not already running.
    if not display_running:
        console.fancy_print("<INFO>Starting display thread...</INFO>")
        threading.Thread(target=display_frames, daemon=True).start()
        
        # Wait until the display thread sets its running flag.
        while not display_running:
            pass
        console.fancy_print("<GOOD>Display thread started.</GOOD>")

    # Pause execution until the user presses Enter, allowing them to read the console output.
    console.press_enter_pause()

if __name__ == "__main__":

    # Keep the main thread alive.
    try:
        while True:
            _, selection = console.integer_only_menu_with_validation("vision processor", ["start", "toggle video processing", "relaunch display window", "exit"])

            if selection == 'start':
                start_threads()

            if selection == 'toggle video processing':
                no_video_processing = not no_video_processing

            if selection == 'relaunch display window':
                if not display_running:
                    threading.Thread(target=display_frames, daemon=True).start()

            if selection == 'exit':
                console.fancy_print("<GOOD>Exiting...</GOOD>")
                break
    except:
        exit()