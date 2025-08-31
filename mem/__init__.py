from typing import Any, Optional


class service:
    url: str
    status: Optional[int]
    online: bool
    public: bool
    error: Optional[str]
    ping: Optional[int]

    def __init__(
        self,
        url: str = "",
        label: str = "",
        public: bool = True,
    ):
        self.url = url
        self.public = public
        self.label = label

        self.online = False
        self.status = None
        self.error = None
        self.ping = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status,
            "public": self.public,
            "online": self.online,
            "error": self.error,
            "ping": self.ping,
            "label": self.label,
        }

    def set_status(self, status: Optional[int]):
        self.status = status

    def set_online(self, b: bool):
        self.online = b

    def set_error(self, s: Optional[str]):
        self.error = s

    def set_ping(self, n: Optional[int]):
        self.ping = n


services: list[service] = [
    service("https://git.ihatemen.uk/", "Gitea"),
    service("https://plex.ihatemen.uk/", "Plex"),
    service("https://truenas.local/", "TrueNAS", False),
    service("https://cloud.ihatemen.uk/", "NextCloud"),
    service("https://request.ihatemen.uk/", "Overseerr"),
    service("https://id.ihatemen.uk/", "PocketID"),
    service("http://tautulli.local", "Tautulli", False),
    service("https://transmission.local", "Transmission", False),
    service("https://vault.ihatemen.uk", "Vault Warden"),
    service("https://nginx.local", "Nginx (NPM)", False),
]
