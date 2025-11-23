# webgl_spoof_cloud.py
import json

def build_webgl_spoof_script_cloud(profile):

    spoof_vendor = profile.webgl_vendor
    spoof_renderer = profile.webgl_renderer
    spoof_max_texture_size = 16384

    # viewport from profile (browser will be set to same size)
    w, h = profile.viewport

    # plausible extension list
    spoof_extensions = [
        "OES_texture_float",
        "OES_texture_half_float",
        "OES_element_index_uint",
        "OES_standard_derivatives",
        "OES_vertex_array_object",
        "WEBGL_debug_renderer_info",
        "WEBGL_debug_shaders",
        "WEBGL_lose_context",
        "WEBGL_depth_texture",
        "EXT_texture_filter_anisotropic"
    ]

    script = f"""
(function() {{
  const SPOOFED_VENDOR = {json.dumps(spoof_vendor)};
  const SPOOFED_RENDERER = {json.dumps(spoof_renderer)};
  const SPOOFED_MAX_TEXTURE_SIZE = {spoof_max_texture_size};
  const SPOOFED_MAX_VIEWPORT_DIMS = [{w}, {h}];
  const SPOOFED_EXTENSIONS = {json.dumps(spoof_extensions)};

  const UNMASKED_VENDOR_WEBGL = 0x9245;
  const UNMASKED_RENDERER_WEBGL = 0x9246;

  function patchContextPrototype(proto) {{
    if (!proto) return;

    const originalGetParameter = proto.getParameter;
    const originalGetSupportedExtensions = proto.getSupportedExtensions;
    const originalGetExtension = proto.getExtension;

    proto.getParameter = function(param) {{
      try {{
        if (param === UNMASKED_VENDOR_WEBGL) return SPOOFED_VENDOR;
        if (param === UNMASKED_RENDERER_WEBGL) return SPOOFED_RENDERER;

        if (param === this.MAX_TEXTURE_SIZE) return SPOOFED_MAX_TEXTURE_SIZE;
        if (param === this.MAX_VIEWPORT_DIMS) return SPOOFED_MAX_VIEWPORT_DIMS;
      }} catch (_) {{}}

      return originalGetParameter.apply(this, arguments);
    }};

    proto.getSupportedExtensions = function() {{
      const native = originalGetSupportedExtensions
        ? (originalGetSupportedExtensions.apply(this, arguments) || [])
        : [];
      const set = new Set(native);
      SPOOFED_EXTENSIONS.forEach(ext => set.add(ext));
      set.add("WEBGL_debug_renderer_info");
      return Array.from(set);
    }};

    proto.getExtension = function(name) {{
      if (name === "WEBGL_debug_renderer_info") {{
        const ext = originalGetExtension
          ? (originalGetExtension.apply(this, arguments) || {{}})
          : {{}};
        ext.UNMASKED_VENDOR_WEBGL = UNMASKED_VENDOR_WEBGL;
        ext.UNMASKED_RENDERER_WEBGL = UNMASKED_RENDERER_WEBGL;
        return ext;
      }}
      return originalGetExtension
        ? originalGetExtension.apply(this, arguments)
        : null;
    }};
  }}

  if (window.WebGLRenderingContext)
    patchContextPrototype(WebGLRenderingContext.prototype);

  if (window.WebGL2RenderingContext)
    patchContextPrototype(WebGL2RenderingContext.prototype);
}})();
"""

    return script
