import threading
import queue
from my_little_snake_helpers.console import Console
from processor import Processor
from display import Display
from capture import Capture

# Global variables.
frame_queue = queue.Queue(maxsize=10)
processed_queue = queue.Queue(maxsize=10)

# Flags for inter-thread communication.
thread_flags = {
    'capture_running': False,
    'processing_running': False,
    'display_running': False
}

processor_flags = {
    'flip_horizontally': False,
    'black_and_white': False,
    'gausian_blur': False,
    'motion_detect': False
}

# Initialize the console for output.
console = Console()

# Initialize the processor with the thread flags and frame queue, processed queue, and console.
processor = Processor(thread_flags, processor_flags, frame_queue, processed_queue, console)

# Initialize the display with the thread flags, frame queue, processed queue, and console.
display = Display(thread_flags, frame_queue, processed_queue, console)

# Initialize the capture routine with the thread flags, frame queue, processed queue, and console.
capture = Capture(thread_flags, frame_queue, processed_queue, console)


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

def frame_processor_menu():

    while True:

        # If the black and white filter is not enabled, the motion detection option should not be available.
        _, selection = console.integer_only_menu_with_validation("frame processor menu", ["flip horizontally", "b/w", "gaussian blur", "motion detect", "back"])

        if selection == 'flip horizontally':
            processor_flags['flip_horizontally'] = not processor_flags['flip_horizontally']
        
        if selection == 'b/w':
            processor_flags['black_and_white'] = not processor_flags['black_and_white']

        if selection == 'gaussian blur':
            processor_flags['gausian_blur'] = not processor_flags['gausian_blur']

        if selection == 'motion detect':
            processor_flags['motion_detect'] = not processor_flags['motion_detect']

        if selection == 'back':
            break


if __name__ == "__main__":
    
    start_threads()
    # Keep the main thread alive.
    try:
        while True:

            _, selection = console.integer_only_menu_with_validation("vision processor", ["frame processor menu", "relaunch display window", "exit"])

            if selection == 'frame processor menu':
                frame_processor_menu()

            if selection == 'relaunch display window':
                if not thread_flags['display_running']:
                    threading.Thread(target=display.display_frames, daemon=True).start()

            if selection == 'exit':
                console.fancy_print("<GOOD>exiting...</GOOD>")
                break
    except:
        exit()