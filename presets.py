# presets.py
# Preset configurations for different musical styles
# Useful for quick AR demonstrations

PRESETS = {
    "trap": {
        "kick": "heavy 808 kick drum, punchy and deep, tight bass thud, seamless loop",
        "snare": "crisp trap snare with snap, layered clap, seamless loop",
        "hihat": "rapid hi-hat rolls, trap style, metallic, seamless loop",
        "bass": "wobbling 808 bass, distorted sub frequencies, seamless loop",
        "atmosphere": "dark ambient pad, minor key, atmospheric, seamless loop",
        "synth": "digital synth stab, aggressive and sharp, seamless loop",
        "clap": "layered trap clap, reverb tail, punchy, seamless loop",
        "arp": "melodic trap bells, icy and bright, arpeggio pattern, seamless loop",
    },
    
    "lofi": {
        "kick": "soft lo-fi kick, warm and muffled, vinyl texture, seamless loop",
        "snare": "dusty snare, low-fi crackling texture, gentle, seamless loop",
        "hihat": "lo-fi hi-hat, slightly off-time, jazzy feel, seamless loop",
        "bass": "warm upright bass, jazzy walking pattern, seamless loop",
        "atmosphere": "vinyl crackle and rain sounds, cozy atmosphere, seamless loop",
        "synth": "rhodes piano chord, warm and nostalgic, seamless loop",
        "clap": "soft hand clap, organic and gentle, seamless loop",
        "arp": "music box melody, delicate and dreamy, seamless loop",
    },
    
    "techno": {
        "kick": "pounding techno kick, industrial and hard, 4/4 pattern, seamless loop",
        "snare": "metallic techno snare, sharp and cutting, seamless loop",
        "hihat": "fast techno hi-hats, machine-like precision, seamless loop",
        "bass": "driving techno bassline, hypnotic and repetitive, seamless loop",
        "atmosphere": "warehouse reverb, industrial ambience, seamless loop",
        "synth": "acid synth sequence, squelchy 303-style, seamless loop",
        "clap": "dry techno clap, minimal and precise, seamless loop",
        "arp": "arpeggiated synth sequence, pulsing and energetic, seamless loop",
    },
    
    "ambient": {
        "kick": "soft ambient kick, distant and ethereal, seamless loop",
        "snare": "gentle percussion, ambient texture, seamless loop",
        "hihat": "shimmering ambient percussion, delicate chimes, seamless loop",
        "bass": "deep drone bass, evolving harmonics, meditative, seamless loop",
        "atmosphere": "expansive ambient pad, celestial and vast, seamless loop",
        "synth": "evolving synth texture, warm and enveloping, seamless loop",
        "clap": "soft hand percussion, organic ambient texture, seamless loop",
        "arp": "slow arpeggio, peaceful and floating, seamless loop",
    },
}


def get_preset(name: str) -> dict:
    """Get a preset by name, returns empty dict if not found."""
    return PRESETS.get(name.lower(), {})


def list_presets() -> list:
    """Return list of available preset names."""
    return list(PRESETS.keys())