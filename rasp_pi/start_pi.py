# start_pi.py
import requests

from profiles.profile_generator import generate_random_profile
from profiles.profile import BrowserProfile


def main():

    # Generate the profile
    raw = generate_random_profile()
    profile = BrowserProfile(**raw)

    print("\n=== Generated Browser Profile ===")
    for k, v in profile.__dict__.items():
        print(f"{k}: {v}")
    print("=================================\n")

    print("[PI] Sending profile to cloud automation server...")

    resp = requests.post(
        "https://rasp-pi.fly.dev/run_flow",
        json=profile.__dict__,
        timeout=90
    )

    print("[PI] Cloud response:", resp.json())
    return

if __name__ == "__main__":
    main()
