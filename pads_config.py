# pads_config.py
# Central configuration for all 8 beat pads.
# Each pad has a unique ID, display label, color hint (for LightGuide), and a default ElevenLabs SFX prompt.
# Edit the prompts here to change the default sounds generated at startup.

PADS = [
    {
        "id": "kick",
        "label": "Kick",
        "color": "#FF4444",  # red
        "prompt": "heavy 808 kick drum, punchy and deep, tight bass thud, seamless loop",
    },
    {
        "id": "snare",
        "label": "Snare",
        "color": "#FF8C00",  # orange
        "prompt": "crisp snare crack, tight snap, punchy attack, seamless loop",
    },
    {
        "id": "hihat",
        "label": "Hi-Hat",
        "color": "#FFD700",  # yellow
        "prompt": "shimmering closed hi-hat, fast metallic rhythm, seamless loop",
    },
    {
        "id": "bass",
        "label": "Bass",
        "color": "#00CC66",  # green
        "prompt": "deep sub bass drone, warm and rumbling, seamless loop",
    },
    {
        "id": "atmosphere",
        "label": "Atmos",
        "color": "#00BFFF",  # blue
        "prompt": "lo-fi vinyl crackle atmosphere, dusty and warm, seamless loop",
    },
    {
        "id": "synth",
        "label": "Synth",
        "color": "#9B59B6",  # purple
        "prompt": "retro 80s synth chord stab, lush and bright, seamless loop",
    },
    {
        "id": "clap",
        "label": "Clap",
        "color": "#E91E8C",  # pink
        "prompt": "funky clap rhythm, snappy and dry, seamless loop",
    },
    {
        "id": "arp",
        "label": "Arp",
        "color": "#1EC9E9",  # cyan
        "prompt": "melodic arpeggio loop, dreamy and ethereal, rising and falling, seamless loop",
    },
]

# Quick lookup by pad ID
PADS_BY_ID = {pad["id"]: pad for pad in PADS}