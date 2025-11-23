## Raspberry Pi Execution Flow

Raspberry Pi
    ↓ generates random fingerprint (UA, WebGL, seeds, viewport, etc.)
    ↓ sends profile JSON → Cloud server
Cloud Server
    ↓ receives profile
    ↓ launches Chrome with spoofing
    ↓ solves CAPTCHA
    ↓ returns result to Pi
