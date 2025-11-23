# profile.py
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class BrowserProfile:
    name: str                   
    version: str                
    os: str                     
    hardware_type: str          
    user_agent: str
    language: str
    timezone: str
    viewport: Tuple[int, int]
    webgl_vendor: str
    webgl_renderer: str
    canvas_seed: int
    audio_seed: int
    tls_client_name: str
    proxy: Optional[tuple]       
