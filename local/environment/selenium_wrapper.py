# selenium_wrapper.py
from selenium_uniq_driver import UniqDriver, HardwareType, SoftwareName, OperatingSystem
from .webgl_spoof import build_webgl_spoof_script

def create_selenium_driver(profile):
    # Map OS → selenium-uniq-driver enum
    os_map = {
        "windows": OperatingSystem.WINDOWS,
        "android": OperatingSystem.ANDROID
    }

    hardware_map = {
        "desktop": HardwareType.COMPUTER,
        "mobile": HardwareType.MOBILE
    }

    driver_creator = UniqDriver(
        hardware_type=hardware_map[profile.hardware_type],
        software_name=SoftwareName.CHROME,   # uniq-driver only supports Chrome
        operating_system=os_map.get(profile.os, OperatingSystem.WINDOWS)
    )

    # Optional proxy
    if profile.proxy:
        host, port, user, password = profile.proxy
        driver_creator.set_proxy(host, port, user, password, "http")

    # Entropy modules activates fingerprint spoofing
    entropy = [
        "user_agent_and_language",
        "device_viewport",
        "device_timezone",
        "canvas_fingerprint",
        "audio_fingerprint"
    ]

    driver = driver_creator.create(entropy)

    # Explicitly override UA
    try:
        driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {"userAgent": profile.user_agent}
        )
    except:
        pass

    # Inject WebGL spoofing script on every new doc
    spoof_script = build_webgl_spoof_script(profile)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": spoof_script}
    )

    # Apply viewport
    w, h = profile.viewport
    driver.set_window_size(w, h)

    return driver
