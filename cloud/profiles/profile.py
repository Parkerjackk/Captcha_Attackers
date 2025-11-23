# profile.py
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class BrowserProfile:
    name: str                    # chrome, edge, etc.
    version: str                 # "120", "17.2", etc.
    os: str                      # windows, android
    hardware_type: str          # desktop or mobile
    user_agent: str
    language: str
    timezone: str
    viewport: Tuple[int, int]
    webgl_vendor: str
    webgl_renderer: str
    canvas_seed: int
    audio_seed: int
    tls_client_name: str
    proxy: Optional[tuple]       # (host, port, user, pass) or None
