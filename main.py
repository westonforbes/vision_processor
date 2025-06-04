import cv2
import threading
import queue
from my_little_snake_helpers.console import Console
from processor import Processor

# Global variables.
frame_queue = queue.Queue(maxsize=10)
processed_queue = queue.Queue(maxsize=10)
previous_frame = None


thread_flags = {
    'capture_running': False,
    'processing_running': False,
    'display_running': False,
    'no_video_processing': True
}

# Initialize the console for output.
console = Console()

# Initialize the processor with the thread flags and frame queue.
processor = Processor(thread_flags, frame_queue, processed_queue, console)

def capture_frames():

    # Access global variables to indicate that the capture thread is running and for the frame queue.
    global thread_flags, frame_queue, console
    
    # Initialize video capture from the default camera using DirectShow.
    # cap = cv2.VideoCapture(0) # Default backend
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Using DirectShow for potentially better compatibility/performance on Windows.
    
    while True:
        
        # Indicate the capture thread is running.
        thread_flags['capture_running'] = True

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
    thread_flags['capture_running'] = False
    console.fancy_print("<INFO>capture thread stopped.</INFO>")


def display_frames():

    # Access the global variable to indicate that the display thread is running.
    global thread_flags
    
    while True:

        # Indicate the display thread is running.
        thread_flags['display_running'] = True

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
    thread_flags['display_running'] = False


def start_threads():
    # Access global variables to control thread startup and for console output.
    global thread_flags, console
    
    # Clear the console for a cleaner output.
    console.clear()
    
    # Start the capture thread if it's not already running.
    if not thread_flags['capture_running']:
        console.fancy_print("<INFO>Starting capture thread...</INFO>")
        threading.Thread(target=capture_frames, daemon=True).start()
        
        # Wait until the capture thread sets its running flag.
        while not thread_flags['capture_running']:
            pass
        console.fancy_print("<GOOD>Capture thread started.</GOOD>")

    # Start the processing thread if it's not already running.
    if not thread_flags['processing_running']:
        console.fancy_print("<INFO>Starting processing thread...</INFO>")
        threading.Thread(target=processor.process_frames, daemon=True).start()
        
        # Wait until the processing thread sets its running flag.
        while not thread_flags['processing_running']:
            pass
        console.fancy_print("<GOOD>Processing thread started.</GOOD>")

    # Start the display thread if it's not already running.
    if not thread_flags['display_running']:
        console.fancy_print("<INFO>Starting display thread...</INFO>")
        threading.Thread(target=display_frames, daemon=True).start()
        
        # Wait until the display thread sets its running flag.
        while not thread_flags['display_running']:
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
                thread_flags['no_video_processing'] = not thread_flags['no_video_processing']

            if selection == 'relaunch display window':
                if not thread_flags['display_running']:
                    threading.Thread(target=display_frames, daemon=True).start()

            if selection == 'exit':
                console.fancy_print("<GOOD>exiting...</GOOD>")
                break
    except:
        exit()