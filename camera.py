import signal
import threading
import subprocess
from my_little_snake_helpers.console import Console

class Camera():
    def __init__(self):
        self.active = False
        self.streamer_thread = None
        self.process = None
        self.console = Console()

    def run_streamer(self):
        
        # Try protect launching the mjpg_streamer command.
        try:

            # Start a new thread to run the mjpg_streamer command. Suppress output.
            self.process = subprocess.Popen([
                "/mjpg-streamer/mjpg-streamer-experimental/mjpg_streamer",
                "-i", "/mjpg-streamer/mjpg-streamer-experimental/input_uvc.so",
                "-o", "/mjpg-streamer/mjpg-streamer-experimental/output_http.so -w /mjpg-streamer/mjpg-streamer-experimental/www"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for the process to complete.
            self.process.wait()

        # If an error occurs, print the error message.
        except Exception as e:
            self.console.fancy_print(f"<BAD>mjpg_streamer failed: {e}</BAD>")

    def activate(self):
        self.active = True
        self.streamer_thread = threading.Thread(target=self.run_streamer, daemon=True)
        self.streamer_thread.start()

    def deactivate(self):
        self.active = False
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                self.console.fancy_print(f"<BADfailed to terminate mjpg_streamer: {e}</BAD>")
