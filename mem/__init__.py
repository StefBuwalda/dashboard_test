from typing import Any, Optional


class service:
    id: int
    url: str
    status: Optional[int]
    online: bool
    public: bool
    error: Optional[str]
    ping: Optional[int]
    icon_filetype: str
    ping_type: int

    def __init__(
        self,
        id: int,
        url: str = "",
        label: str = "",
        public: bool = True,
        icon_filetype: str = "svg",
        ping_type: int = 0,
    ):
        self.id = id
        self.url = url
        self.public = public
        self.label = label
        self.ping_type = ping_type

        self.online = False
        self.status = None
        self.error = None
        self.ping = None
        self.icon_filetype = icon_filetype

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status,
            "public": self.public,
            "online": self.online,
            "error": self.error,
            "ping": self.ping,
            "label": self.label,
            "icon_filetype": self.icon_filetype,
            "id": self.id,
            "ping_type": self.ping_type,
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
    service(0, "https://git.ihatemen.uk/", "Gitea"),
    service(1, "https://plex.ihatemen.uk/", "Plex"),
    service(2, "https://truenas.local/", "TrueNAS", False),
    service(3, "https://cloud.ihatemen.uk/", "NextCloud"),
    service(4, "https://request.ihatemen.uk/", "Overseerr"),
    service(5, "https://id.ihatemen.uk/", "PocketID"),
    service(6, "http://tautulli.local", "Tautulli", False),
    service(
        7, "https://transmission.local", "Transmission", False, ping_type=1
    ),
    service(8, "https://vault.ihatemen.uk", "Vault Warden"),
    service(9, "https://nginx.local", "Nginx (NPM)", False),
]
