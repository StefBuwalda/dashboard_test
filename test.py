import time
import requests
import traceback
import urllib3
from urllib.parse import urlparse
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

services = [
    "https://truenas.local/",
    "https://example.com/",
    "https://git.ihatemen.uk/"
]

services_status = {}

# Determine SSL verification based on hostname
def should_verify_ssl(url: str):
    hostname = urlparse(url).hostname
    return not (hostname and hostname.endswith(".local"))

# Function to check a single service
def check_service(url: str) -> tuple[str, dict[str, Any]]:
    try:
        start = time.time()
        r = requests.head(url, allow_redirects=True, timeout=5, verify=should_verify_ssl(url))
        latency = int((time.time() - start) * 1000)
        return url, {
            "status": "up" if r.ok else "down",
            "latency": latency,
            "error": None
        }
    except requests.exceptions.RequestException as e:
        return url, {
            "status": "down",
            "latency": None,
            "error": str(e),
            "trace": traceback.format_exc()
        }

# Background thread that checks all services in parallel
def check_services_periodically(interval: int=5):
    while True:
        with ThreadPoolExecutor(max_workers=len(services)) as executor:
            futures = [executor.submit(check_service, url) for url in services]
            for future in as_completed(futures):
                url, result = future.result()
                services_status[url] = result
        time.sleep(interval)

# Start background checker
import threading
threading.Thread(target=check_services_periodically, daemon=True).start()

# Flask app to serve status
app = Flask(__name__)

@app.route("/status")
def status():
    return jsonify(services_status)

if __name__ == "__main__":
    app.run(debug=True)
