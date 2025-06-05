import threading
import queue
from my_little_snake_helpers.console import Console
from processor import Processor
from display import Display
from capture import Capture

# Global variables.
frame_queue = queue.Queue(maxsize=10)
processed_queue = queue.Queue(maxsize=10)
reference_code = 'qrcode.py'

# Flags for inter-thread communication.
thread_flags = {
    'capture_running': False,
    'processing_running': False,
    'display_running': False
}

# Define the region of interest (ROI) bounds.
roi_bounds = {
    'x1': 100,
    'y1': 100,
    'x2': 300,
    'y2': 300
}

# Define the video capture resolution.
video_capture_resolution = {
    'width': None,
    'height': None
}

# Initialize the console for output.
console = Console()

# Initialize the processor with the thread flags and frame queue, processed queue, and console.
processor = Processor(thread_flags, roi_bounds, frame_queue, processed_queue, console)

# Initialize the display with the thread flags, frame queue, processed queue, and console.
display = Display(thread_flags, frame_queue, processed_queue, console)

# Initialize the capture routine with the thread flags, frame queue, processed queue, and console.
capture = Capture(thread_flags, frame_queue, processed_queue, console, video_capture_resolution)


def start_threads():

    # Start the capture thread if it's not already running.
    if not thread_flags['capture_running']:
        threading.Thread(target=capture.capture_frames, daemon=True).start()
        while not thread_flags['capture_running']:
            pass

    # Start the processing thread if it's not already running.
    if not thread_flags['processing_running']:
        threading.Thread(target=processor.process_frames, daemon=True).start()
        while not thread_flags['processing_running']:
            pass

    # Start the display thread if it's not already running.
    if not thread_flags['display_running']:
        threading.Thread(target=display.display_frames, daemon=True).start()
        while not thread_flags['display_running']:
            pass


if __name__ == "__main__":
    
    start_threads()
    # Keep the main thread alive.
    try:
        while True:

            _, selection = console.integer_only_menu_with_validation("vision processor", ["relaunch display window", "exit"])

            if selection == 'relaunch display window':
                if not thread_flags['display_running']:
                    threading.Thread(target=display.display_frames, daemon=True).start()

            if selection == 'exit':
                console.fancy_print("<GOOD>exiting...</GOOD>")
                break
    except:
        exit()