from mem import services
import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def update_services() -> None:
    print("Updating Service Status")
    while True:
        for s in services:
            try:
                r = requests.head(
                    url=s.url,
                    verify=s.public,
                    allow_redirects=True,
                    timeout=1,
                )
                s.set_status(r.ok)
            except requests.exceptions.RequestException as e:
                print(e)
                s.set_status(False)
        time.sleep(3)
