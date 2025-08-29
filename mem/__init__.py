from typing import Any, Optional


class service:
    url: str
    status: Optional[int]
    online: bool
    public: bool

    def __init__(self, url: str = "", public: bool = True):
        self.url = url
        self.public = public

        self.online = False
        self.status = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status,
            "public": self.public,
            "online": self.online,
        }

    def set_status(self, status: int):
        self.status = status


services: list[service] = [
    service("https://git.ihatemen.uk"),
    service("https://plex.ihatemen.uk"),
    service("https://truenas.local", False),
]
