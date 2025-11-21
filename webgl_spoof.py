# webgl_spoof.py
import json

def build_webgl_spoof_script(profile):
    """
    Generate JavaScript that spoofs WebGL vendor/renderer/capabilities
    based on the given BrowserProfile.
    """

    spoof_vendor = profile.webgl_vendor
    spoof_renderer = profile.webgl_renderer

    # High-end plausible texture size (Chrome often reports 16384)
    spoof_max_texture_size = 16384

    # Reuse viewport height/width as max dims (realistic enough)
    vw, vh = profile.viewport
    spoof_viewport_w, spoof_viewport_h = vw, vh

    # A plausible extension list
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

    base_js = r"""
(function() {
  const SPOOFED_VENDOR = "__SPOOF_VENDOR__";
  const SPOOFED_RENDERER = "__SPOOF_RENDERER__";
  const SPOOFED_MAX_TEXTURE_SIZE = __SPOOF_MAX_TEXTURE_SIZE__;
  const SPOOFED_MAX_VIEWPORT_DIMS = [__SPOOF_VIEWPORT_W__, __SPOOF_VIEWPORT_H__];
  const SPOOFED_EXTENSIONS = __SPOOF_EXTENSIONS_ARRAY__;

  const UNMASKED_VENDOR_WEBGL = 0x9245;
  const UNMASKED_RENDERER_WEBGL = 0x9246;

  function patchContextPrototype(proto) {
    if (!proto) return;

    const originalGetParameter = proto.getParameter;
    const originalGetSupportedExtensions = proto.getSupportedExtensions;
    const originalGetExtension = proto.getExtension;

    proto.getParameter = function(param) {
      try {
        if (param === UNMASKED_VENDOR_WEBGL) return SPOOFED_VENDOR;
        if (param === UNMASKED_RENDERER_WEBGL) return SPOOFED_RENDERER;

        if (typeof this.MAX_TEXTURE_SIZE !== "undefined" &&
            param === this.MAX_TEXTURE_SIZE) {
          return SPOOFED_MAX_TEXTURE_SIZE;
        }
        if (typeof this.MAX_VIEWPORT_DIMS !== "undefined" &&
            param === this.MAX_VIEWPORT_DIMS) {
          return SPOOFED_MAX_VIEWPORT_DIMS;
        }
      } catch (_) {}

      return originalGetParameter.apply(this, arguments);
    };

    proto.getSupportedExtensions = function() {
      const native = originalGetSupportedExtensions
        ? (originalGetSupportedExtensions.apply(this, arguments) || [])
        : [];
      const set = new Set(native);
      SPOOFED_EXTENSIONS.forEach(ext => set.add(ext));
      set.add("WEBGL_debug_renderer_info");
      return Array.from(set);
    };

    proto.getExtension = function(name) {
      if (name === "WEBGL_debug_renderer_info") {
        const ext = originalGetExtension
          ? (originalGetExtension.apply(this, arguments) || {})
          : {};
        ext.UNMASKED_VENDOR_WEBGL = UNMASKED_VENDOR_WEBGL;
        ext.UNMASKED_RENDERER_WEBGL = UNMASKED_RENDERER_WEBGL;
        return ext;
      }
      return originalGetExtension
        ? originalGetExtension.apply(this, arguments)
        : null;
    };
  }

  if (window.WebGLRenderingContext)
    patchContextPrototype(WebGLRenderingContext.prototype);

  if (window.WebGL2RenderingContext)
    patchContextPrototype(WebGL2RenderingContext.prototype);
})();
"""

    js = (
        base_js
            .replace("__SPOOF_VENDOR__", json.dumps(spoof_vendor))
            .replace("__SPOOF_RENDERER__", json.dumps(spoof_renderer))
            .replace("__SPOOF_MAX_TEXTURE_SIZE__", str(spoof_max_texture_size))
            .replace("__SPOOF_VIEWPORT_W__", str(spoof_viewport_w))
            .replace("__SPOOF_VIEWPORT_H__", str(spoof_viewport_h))
            .replace("__SPOOF_EXTENSIONS_ARRAY__", json.dumps(spoof_extensions))
    )

    return js
