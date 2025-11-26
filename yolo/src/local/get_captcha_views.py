# get_captcha_views.py

import asyncio
from pathlib import Path
from urllib.parse import urlparse, urlunparse, urlencode

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEFAULT_ANGLES = [(rx, ry) for rx in range(-75, 76, 15) for ry in range(-75, 76, 15)]


async def download_captcha_views(driver, tls_client, out_dir, angles: list[tuple[int, int]] | None = None, max_concurrent: int = 16) -> None:
    """
    1. Find the captcha <img> on the page and read its src, like for example
       https://group4.kokax.com/api/captcha/image/<uuid>?rotX=-20&rotY=22
    2. Strip query params and re-call it for all (rotX, rotY) in 'angles'
       using the same cookies + UA as the browser
    3. Save each PNG into out_dir as rx{rx}_ry{ry}.png
    """

    if angles is None:
        angles = DEFAULT_ANGLES

    # Fresh directory for this session
    out_dir = Path(out_dir)
    if out_dir.exists():
        for p in out_dir.iterdir():
            if p.is_file():
                p.unlink()
    else:
        out_dir.mkdir(parents=True, exist_ok=True)

    # Wait for the captcha image to be visible and grab its src URL
    img_elem = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "img[src*='/api/captcha/image']")
        )
    )
    img_src = img_elem.get_attribute("src")

    # Strip any existing rotX and rotY values
    parsed = urlparse(img_src)
    base_url = urlunparse(parsed._replace(query=""))

    # Copy cookies from Selenium into a Cookie header for tls_client
    cookies = driver.get_cookies()
    cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in cookies) if cookies else ""

    headers = {
        # keep the browser UA so backend sees a consistent client
        "User-Agent": driver.execute_script("return navigator.userAgent"),
    }
    if cookie_header:
        headers["Cookie"] = cookie_header

    sem = asyncio.Semaphore(max_concurrent)

    async def fetch_angle(rx: int, ry: int) -> None:
       # Fetch a single view and save it
        q = urlencode({"rotX": rx, "rotY": ry})
        url = f"{base_url}?{q}"

        async with sem:
            try:
                resp = await tls_client.get(url, headers=headers)
            except Exception as e:
                print(f"[WARN] exception fetching rx={rx}, ry={ry}: {e}")
                return

            status = getattr(resp, "status_code", None) or getattr(resp, "status", None)
            content = getattr(resp, "content", None) or getattr(resp, "body", None)

            if status != 200 or not content:
                print(f"[WARN] failed to fetch view rx={rx}, ry={ry}, status={status}")
                return

            out_path = out_dir / f"rx{rx}_ry{ry}.png"
            out_path.write_bytes(content)

    # Kick off all requests concurrently (bounded by semaphore)
    tasks = [fetch_angle(rx, ry) for rx, ry in angles]
    await asyncio.gather(*tasks)
