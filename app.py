from app.flask_app import start_flask, stop_event as flask_stop
from app.aio_client import start_worker, stop_event as aio_stop
import threading
import sys
import time

# Only run if directly running file
if __name__ == "__main__":
    threading.Thread(target=start_worker, daemon=True).start()

    threading.Thread(target=start_flask, daemon=True).start()

    # Optional: monitor stop_event in a separate thread
    def monitor_worker():
        while not aio_stop.is_set() and not flask_stop.is_set():
            time.sleep(1)
        print("Worker failed, stopping program...")
        sys.exit(1)

    monitor_worker()
