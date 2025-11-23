# canvas_spoof_cloud.py

def build_canvas_spoof_script(profile):

    seed = profile.canvas_seed

    script = f"""
(function() {{
  function noise() {{
    return {seed} % 10;  // deterministic small noise based on seed
  }}

  const toDataURL = HTMLCanvasElement.prototype.toDataURL;
  HTMLCanvasElement.prototype.toDataURL = function() {{
    const ctx = this.getContext('2d');
    if (ctx) {{
      const w = this.width, h = this.height;
      const img = ctx.getImageData(0, 0, w, h);
      for (let i = 0; i < img.data.length; i += 4) {{
        img.data[i]   += noise();
        img.data[i+1] += noise();
        img.data[i+2] += noise();
      }}
      ctx.putImageData(img, 0, 0);
    }}
    return toDataURL.apply(this, arguments);
  }};

  const toBlob = HTMLCanvasElement.prototype.toBlob;
  HTMLCanvasElement.prototype.toBlob = function(cb, type, quality) {{
    const ctx = this.getContext('2d');
    if (ctx) {{
      const w = this.width, h = this.height;
      const img = ctx.getImageData(0, 0, w, h);
      for (let i = 0; i < img.data.length; i += 4) {{
        img.data[i]   += noise();
        img.data[i+1] += noise();
        img.data[i+2] += noise();
      }}
      ctx.putImageData(img, 0, 0);
    }}
    return toBlob.apply(this, arguments);
  }};
}})();
"""
    return script
