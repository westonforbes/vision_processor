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

# Flags for the frame processor.
processor_flags = {
    'flip_horizontally': False,
    'black_and_white': False,
    'gaussian_blur': False,
    'motion_detect': False,
    'dialate': False,
    'mog2_motion_detect': False,
    'roi_enabled': False,

    'gausion_blur_settings': {
        'kernel_size': (5, 5)
    }
}

# Define the region of interest (ROI) bounds.
roi_bounds = {
    'x1': 100,
    'y1': 100,
    'x2': 400,
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
processor = Processor(thread_flags, processor_flags, roi_bounds, frame_queue, processed_queue, console)

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


def menu_roi_customization():
    
    while True:
        
        _, selection = console.integer_only_menu_with_validation("roi customization", ["set x1", "set y1", "set x2", "set y2", "back"])
        
        if selection == 'set x1':
            x1 = console.fancy_input("enter x1 coordinate (current: {}): ".format(roi_bounds['x1']))
            roi_bounds['x1'] = int(x1)
            
        if selection == 'set y1':
            y1 = console.fancy_input("enter y1 coordinate (current: {}): ".format(roi_bounds['y1']))
            roi_bounds['y1'] = int(y1)
            
        if selection == 'set x2':
            x2 = console.fancy_input("enter x2 coordinate (current: {}): ".format(roi_bounds['x2']))
            roi_bounds['x2'] = int(x2)
            
        if selection == 'set y2':
            y2 = console.fancy_input("enter y2 coordinate (current: {}): ".format(roi_bounds['y2']))
            roi_bounds['y2'] = int(y2)
            
        if selection == 'back':
            break

def menu_guassian_blur():
    while True:
        
        _, selection = console.integer_only_menu_with_validation("gaussian blur settings", ["set kernel size x", "set kernel size y", "back"])
        
        if selection == 'set kernel size x':
            x = console.fancy_input("enter x size (current: {}): ".format(processor_flags['gausion_blur_settings']['kernel_size'][0]))
            processor_flags['gausion_blur_settings']['kernel_size'][0] = int(x)
            
        if selection == 'set kernel size y':
            x = console.fancy_input("enter y size (current: {}): ".format(processor_flags['gausion_blur_settings']['kernel_size'][1]))
            processor_flags['gausion_blur_settings']['kernel_size'][1] = int(1)

        if selection == 'back':
            break

# Solid, commented, keep collapsed.
def menu_frame_processor():

    # Function to create the menu options based on the current processor flags.
    def create_menu_frame_processor_options():
        menu_items = []

        # Menu item 1.
        if processor_flags['flip_horizontally']: menu_items.append("<GOOD>flip horizontally - enabled</GOOD>")
        else: menu_items.append("flip horizontally - disabled")

        # Menu item 2.
        if processor_flags['black_and_white']: menu_items.append("<GOOD>black and white filter - enabled</GOOD>")
        else: menu_items.append("black and white filter - disabled")

        # Menu item 3.
        if processor_flags['gaussian_blur']: menu_items.append("<GOOD>gaussian blur - enabled</GOOD>")
        else: menu_items.append("gaussian blur - disabled")

        # Menu item 4.
        if processor_flags['motion_detect']: menu_items.append("<GOOD>motion detect - enabled</GOOD>")
        else: menu_items.append("motion detect - disabled")

        # Menu item 5.
        if processor_flags['dialate']: menu_items.append("<GOOD>dialate - enabled</GOOD>") 
        else: menu_items.append("dialate - disabled")

        # Menu item 6.
        if processor_flags['mog2_motion_detect']: menu_items.append("<GOOD>advanced motion detection - enabled</GOOD>")
        else: menu_items.append("advanced motion detection - disabled")

        # Menu item 7.
        if processor_flags['roi_enabled']: menu_items.append("<GOOD>roi overlay - enabled</GOOD>")
        else: menu_items.append("roi overlay - disabled")

        # Menu item 8.
        menu_items.append("roi customization")

        # Menu item 9.
        menu_items.append("back")

        return menu_items

    # Loop until the user chooses to exit.
    while True:

        # Create the menu options, text changes based on the current flags.
        menu_items = create_menu_frame_processor_options()

        # Generate the menu and get the user's selection.
        selection_int, selection_str = console.integer_only_menu_with_validation("frame processor menu", menu_items)

        # Since the text changes based on the flags, we need to check the selection based off the integer value of the selection.

        # Toggle the flags based on the user's selection.
        if selection_int == 1:
            processor_flags['flip_horizontally'] = not processor_flags['flip_horizontally']
        
        if selection_int == 2:
            processor_flags['black_and_white'] = not processor_flags['black_and_white']

        if selection_int == 3:
            processor_flags['gaussian_blur'] = not processor_flags['gaussian_blur']

        if selection_int == 4:
            processor_flags['motion_detect'] = not processor_flags['motion_detect']

        if selection_int == 5:
            processor_flags['dialate'] = not processor_flags['dialate']

        if selection_int == 6:
            processor_flags['mog2_motion_detect'] = not processor_flags['mog2_motion_detect']

        if selection_int == 7:
            processor_flags['roi_enabled'] = not processor_flags['roi_enabled']

        # Access the ROI customization menu.
        if selection_int == 8:
            menu_roi_customization()

        # Exit the frame processor menu.
        if selection_str == 'back':
            break

# Keep collapsed.
if __name__ == "__main__":
    
    start_threads()
    # Keep the main thread alive.
    try:
        while True:

            _, selection = console.integer_only_menu_with_validation("vision processor", ["frame processor menu", "relaunch display window", "exit"])

            if selection == 'frame processor menu':
                menu_frame_processor()

            if selection == 'relaunch display window':
                if not thread_flags['display_running']:
                    threading.Thread(target=display.display_frames, daemon=True).start()

            if selection == 'exit':
                console.fancy_print("<GOOD>exiting...</GOOD>")
                break
    except:
        exit()