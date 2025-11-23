# audio_spoof_cloud.py

def build_audio_spoof_script(profile):

    seed = profile.audio_seed

    script = f"""
(function() {{
  const originalGetChannelData = AudioBuffer.prototype.getChannelData;

  AudioBuffer.prototype.getChannelData = function() {{
    const data = originalGetChannelData.apply(this, arguments);
    for (let i = 0; i < data.length; i += 100) {{
      data[i] = data[i] + (({seed} % 100) / 100000); 
    }}
    return data;
  }};
}})();
"""
    return script
