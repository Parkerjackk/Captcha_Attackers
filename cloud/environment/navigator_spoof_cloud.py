# navigator_spoof_cloud.py

def build_navigator_spoof_script(profile):

    lang = profile.language
    hw = 8  # moderate, realistic core count

    script = f"""
(function() {{
  Object.defineProperty(navigator, 'webdriver', {{
    get: () => false
  }});

  Object.defineProperty(navigator, 'languages', {{
    get: () => ['{lang}']
  }});

  Object.defineProperty(navigator, 'platform', {{
    get: () => 'Win32'
  }});

  Object.defineProperty(navigator, 'hardwareConcurrency', {{
    get: () => {hw}
  }});
}})();
"""
    return script
