# profile_factory.py
import random

# --------------------------
# IMPORT ALL YOUR CONSTANTS
# --------------------------

CHROME_VERSIONS = [118, 119, 120, 121, 122, 123, 124, 125]
EDGE_VERSIONS = [120, 121]
CHROME_ANDROID_VERSIONS = [118, 119, 120, 121]
ANDROID_WEBVIEW_VERSIONS = [118]

TZ_US = ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"]
TZ_EU = ["Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Madrid", "Europe/Rome", "Europe/Prague", "Europe/Warsaw"]

DESKTOP_VIEWPORTS = [
    (1920, 1080), (1366, 768), (1536, 864),
    (1680, 1050), (1600, 900), (1920, 1200), (1470, 956)
]

ANDROID_VIEWPORTS = [
    (412, 915), (412, 869), (393, 851)
]

WEBGL_DESKTOP = [
    ("Google Inc.", "ANGLE (NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0)"),
    ("Google Inc.", "ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)"),
    ("Google Inc.", "ANGLE (Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0)")
]

WEBGL_ANDROID = [
    ("Qualcomm", "Adreno (TM) 660"),
    ("Qualcomm", "Adreno (TM) 640"),
    ("Google Inc.", "ANGLE (Google Pixel 6, Vulkan 1.1)")
]

def seed():
    return random.randint(100000, 999999)

# --------------------------
# PROFILE GENERATORS
# --------------------------

def windows_chrome():
    v = str(random.choice(CHROME_VERSIONS))
    ua = (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{v}.0.0.0 Safari/537.36"
    )
    vendor, renderer = random.choice(WEBGL_DESKTOP)

    return {
        "name": "chrome",
        "version": v,
        "os": "windows",
        "hardware_type": "desktop",
        "user_agent": ua,
        "language": random.choice(
            ["en-US", "en-GB", "fr-FR", "de-DE", "es-ES", "it-IT", "pl-PL"]
        ),
        "timezone": random.choice(TZ_US + TZ_EU),
        "viewport": random.choice(DESKTOP_VIEWPORTS),
        "webgl_vendor": vendor,
        "webgl_renderer": renderer,
        "canvas_seed": seed(),
        "audio_seed": seed(),
        "tls_client_name": f"chrome_{v}",
        "proxy": None
    }


def windows_edge():
    v = str(random.choice(EDGE_VERSIONS))
    ua = (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{v}.0.0.0 Safari/537.36 Edg/{v}.0.0.0"
    )
    vendor, renderer = random.choice(WEBGL_DESKTOP)

    return {
        "name": "edge",
        "version": v,
        "os": "windows",
        "hardware_type": "desktop",
        "user_agent": ua,
        "language": random.choice(["en-US", "en-GB"]),
        "timezone": random.choice(TZ_US),
        "viewport": random.choice(DESKTOP_VIEWPORTS),
        "webgl_vendor": vendor,
        "webgl_renderer": renderer,
        "canvas_seed": seed(),
        "audio_seed": seed(),
        "tls_client_name": f"edge_{v}",
        "proxy": None
    }


def android_chrome():
    v = str(random.choice(CHROME_ANDROID_VERSIONS))
    ua = (
        f"Mozilla/5.0 (Linux; Android 13; SM-G991B) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{v}.0.0.0 Mobile Safari/537.36"
    )
    vendor, renderer = random.choice(WEBGL_ANDROID)

    return {
        "name": "chrome_mobile",
        "version": v,
        "os": "android",
        "hardware_type": "mobile",
        "user_agent": ua,
        "language": "en-US",
        "timezone": random.choice(TZ_US + TZ_EU),
        "viewport": random.choice(ANDROID_VIEWPORTS),
        "webgl_vendor": vendor,
        "webgl_renderer": renderer,
        "canvas_seed": seed(),
        "audio_seed": seed(),
        "tls_client_name": f"chrome_{v}_android",
        "proxy": None
    }


def android_webview():
    v = str(random.choice(ANDROID_WEBVIEW_VERSIONS))
    ua = (
        f"Mozilla/5.0 (Linux; Android 11; Mi 9T Pro) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Version/4.0 Chrome/{v}.0.0.0 Mobile Safari/537.36"
    )
    vendor, renderer = random.choice(WEBGL_ANDROID)

    return {
        "name": "android_webview",
        "version": v,
        "os": "android",
        "hardware_type": "mobile",
        "user_agent": ua,
        "language": "es-ES",
        "timezone": random.choice(TZ_EU),
        "viewport": random.choice(ANDROID_VIEWPORTS),
        "webgl_vendor": vendor,
        "webgl_renderer": renderer,
        "canvas_seed": seed(),
        "audio_seed": seed(),
        "tls_client_name": f"android_webview_{v}",
        "proxy": None
    }

# --------------------------------------
# MAIN FACTORY FUNCTION
# --------------------------------------

GENERATORS = [
    windows_chrome,
    windows_edge,
    android_chrome,
    android_webview
]

def generate_random_profile():
    """Return ONE randomly selected profile config."""
    gen = random.choice(GENERATORS)
    return gen()
