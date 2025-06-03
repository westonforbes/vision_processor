import sys
from my_little_snake_helpers.console import Console
from camera import Camera


# Global variables.
console = Console()
camera = Camera()


def present_menu():

    # Initialize the selection variable.
    selection = None

    # If the camera is not active...
    if not camera.active:
        _, selection = console.integer_only_menu_with_validation(title="vision processor", item_list=["activate camera", "exit"],)
        return selection

    # If the camera is active...
    if camera.active:
        _, selection = console.integer_only_menu_with_validation(title="vision processor", item_list=["deactivate camera", "exit"],)
        return selection


def process_selection(selection):
    
    # If the user selected "activate camera"...
    if selection == 'activate camera':
        camera.activate()
    
    # If the user selected "deactivate camera"...
    if selection == 'deactivate camera':
        camera.deactivate()
    
    # If the user selected "exit"...
    if selection == 'exit':
        sys.exit(0)
    

def main():

    # Main loop.
    while True:

        # Present the menu.
        selection = present_menu()

        # Process the selection.
        process_selection(selection)


# Run the main function.
if __name__ == "__main__":
    main()
