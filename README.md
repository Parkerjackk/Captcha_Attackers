# Attackers Module

A modular framework for simulating automated browser activity, environment spoofing, and profile-driven behavior.
Designed for scalability, clean separation of concerns, and easy integration with automated workflows.


## Project Structure

attackers/
│
├── start.py                 # Entry point for running an attack/profile session
│
├── environment/             # Browser, TLS, WebGL, and system-level spoofing
│   ├── selenium_wrapper.py
│   ├── tls_wrapper.py
│   └── webgl_spoof.py
│
├── interactions/            # Human-like interaction simulation
│   └── mouse_movement.py
│
└── profiles/                # Identity/profile generation and management
    ├── profile.py
    └── profile_generator.py

## Modules Overview
### Start Script

**start.py**
Main entry point that initializes profiles, configures the environment, and launches automated interactions.

### Environment Layer

Manages browser capabilities, security layers, and fingerprint spoofing:

 - 'selenium_wrapper.py' — Browser automation wrapper

 - 'tls_wrapper.py' — TLS parameter spoofing

 - 'webgl_spoof.py' — WebGL fingerprint modification

### Interactions

Simulates human-like actions:

mouse_movement.py — Natural mouse movement patterns and paths

### Profiles

Manages identity, device, and session parameters:

 - 'profile.py' — Profile representation

 - 'profile_generator.py' — Generates randomized or configured browser profiles

## Installation
Requires **Python 3.9+**:
'''bash
    pip install -r requirement.txt

## Usage
Run the entry script:

    python start.py