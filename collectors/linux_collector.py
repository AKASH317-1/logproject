import time
import sys
import os
from queue import Queue

def start_linux(log_queue: Queue):
    # Use a test file on Windows, real auth.log on Linux
    if sys.platform == "win32":
        LOG_FILE = "test_auth.log"   # create a dummy file
        # Create a test file if it doesn't exist
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                f.write("Failed password for root from 192.168.1.100\n")
                f.write("Accepted password for admin from 10.0.0.2\n")
    else:
        LOG_FILE = "/var/log/auth.log"

    with open(LOG_FILE, "r") as file:
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.2)
                continue
            log_queue.put(("linux", line.strip()))