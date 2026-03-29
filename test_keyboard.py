# test_keyboard.py
# Keyboard test harness — simulates LightGuide pad taps from your laptop.
# Run this in a SEPARATE terminal while server.py is already running.
#
# Controls:
#   1-8        — toggle pad loop on/off
#   r1-r8      — reprompt a pad  (e.g. "r6")
#   v1-v8      — set volume for a pad (e.g. "v6", then enter 0.0-1.0)
#   t1-t8      — set tempo for a pad (e.g. "t6", then enter 0.25-4.0)
#   ta         — set tempo for ALL pads (then enter 0.25-4.0)
#   tr         — reset tempo (tr6 for one pad, tr for all)
#   s          — show full status of all pads
#   q          — quit

import sys
import requests

SERVER = "http://localhost:5000"

PAD_KEYS = {
    "1": "kick",
    "2": "snare",
    "3": "hihat",
    "4": "bass",
    "5": "atmosphere",
    "6": "synth",
    "7": "clap",
    "8": "arp",
}


def trigger(pad_id):
    try:
        res = requests.post(f"{SERVER}/pad/trigger", json={"pad_id": pad_id})
        data = res.json()
        if res.status_code == 200:
            state = "▶ PLAYING" if data["playing"] else "■ STOPPED"
            print(f"  [{pad_id}] {state}")
        else:
            print(f"  [{pad_id}] Error: {data.get('error')}")
    except requests.ConnectionError:
        print("  ✗ Cannot connect to server. Is server.py running?")


def reprompt(pad_id):
    new_prompt = input(f"  New prompt for '{pad_id}': ").strip()
    if not new_prompt:
        print("  Cancelled.")
        return
    try:
        res = requests.post(f"{SERVER}/pad/reprompt", json={"pad_id": pad_id, "prompt": new_prompt})
        data = res.json()
        if res.status_code == 200:
            key = [k for k, v in PAD_KEYS.items() if v == pad_id][0]
            print(f"  [{pad_id}] Regenerating... press {key} again when ready.")
        else:
            print(f"  [{pad_id}] Error: {data.get('error')}")
    except requests.ConnectionError:
        print("  ✗ Cannot connect to server. Is server.py running?")


def volume(pad_id):
    raw = input(f"  Volume for '{pad_id}' (0.0 - 1.0): ").strip()
    try:
        level = float(raw)
    except ValueError:
        print("  Invalid number. Cancelled.")
        return
    try:
        res = requests.post(f"{SERVER}/pad/volume", json={"pad_id": pad_id, "volume": level})
        data = res.json()
        if res.status_code == 200:
            print(f"  [{pad_id}] Volume set to {data['volume']:.2f}")
        else:
            print(f"  [{pad_id}] Error: {data.get('error')}")
    except requests.ConnectionError:
        print("  ✗ Cannot connect to server. Is server.py running?")


def tempo(pad_id):
    raw = input(f"  Tempo rate for '{pad_id}' (0.25 - 4.0, 1.0 = normal): ").strip()
    try:
        rate = float(raw)
    except ValueError:
        print("  Invalid number. Cancelled.")
        return
    try:
        res = requests.post(f"{SERVER}/pad/tempo", json={"pad_id": pad_id, "rate": rate})
        data = res.json()
        if res.status_code == 200:
            print(f"  [{pad_id}] Tempo set to {data['tempo_rate']:.2f}x")
        else:
            print(f"  [{pad_id}] Error: {data.get('error')}")
    except requests.ConnectionError:
        print("  ✗ Cannot connect to server. Is server.py running?")


def tempo_all():
    raw = input("  Tempo rate for ALL pads (0.25 - 4.0, 1.0 = normal): ").strip()
    try:
        rate = float(raw)
    except ValueError:
        print("  Invalid number. Cancelled.")
        return
    try:
        res = requests.post(f"{SERVER}/tempo/all", json={"rate": rate})
        data = res.json()
        if res.status_code == 200:
            print(f"  All pads set to {data['tempo_rate']:.2f}x")
        else:
            print(f"  Error: {data.get('error')}")
    except requests.ConnectionError:
        print("  ✗ Cannot connect to server. Is server.py running?")


def tempo_reset(pad_id=None):
    try:
        payload = {"pad_id": pad_id} if pad_id else {}
        res = requests.post(f"{SERVER}/tempo/reset", json=payload)
        data = res.json()
        if res.status_code == 200:
            if pad_id:
                print(f"  [{pad_id}] Tempo reset to 1.0x")
            else:
                print(f"  All pads reset to 1.0x")
        else:
            print(f"  Error: {data.get('error')}")
    except requests.ConnectionError:
        print("  ✗ Cannot connect to server. Is server.py running?")


def print_status():
    try:
        res = requests.get(f"{SERVER}/pad/status")
        body = res.json()
        pads = body["pads"]
        print(f"\n  --- PAD STATUS ---")
        for pad in pads:
            play_icon = "▶" if pad["playing"] else "■"
            ready = "" if pad.get("ready") else " (NO AUDIO)"
            regen = " (regenerating...)" if pad["regenerating"] else ""
            vol = f"vol:{pad['volume']:.2f}"
            tempo = f"tempo:{pad['tempo_rate']:.2f}x"
            print(f"  {play_icon} [{pad['id']:12}] {vol}  {tempo}  {pad['prompt'][:35]}{ready}{regen}")
        print()
    except requests.ConnectionError:
        print("  ✗ Cannot connect to server. Is server.py running?")


def print_help():
    print("""
  ┌──────────────────────────────────────────────┐
  │           AR MIXER — KEYBOARD TEST           │
  ├──────────────────────────────────────────────┤
  │  1  Kick        5  Atmosphere                │
  │  2  Snare       6  Synth                     │
  │  3  Hi-Hat      7  Clap                      │
  │  4  Bass        8  Arp                       │
  ├──────────────────────────────────────────────┤
  │  r1-r8  reprompt a pad       (e.g. "r6")     │
  │  v1-v8  set pad volume       (e.g. "v6")     │
  │  t1-t8  set pad tempo        (e.g. "t6")     │
  │  ta     set ALL pads tempo   (e.g. "ta")     │
  │  tr     reset tempo          (tr6 or tr)     │
  │  s      show full status                     │
  │  q      quit                                 │
  └──────────────────────────────────────────────┘
""")


def main():
    print_help()

    while True:
        try:
            key = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting.")
            sys.exit(0)

        if not key:
            continue

        if key == "q":
            print("  Exiting.")
            sys.exit(0)

        elif key == "s":
            print_status()

        elif key == "ta":
            tempo_all()

        # tempo reset: tr or tr1-tr8
        elif key == "tr":
            tempo_reset()
        elif key.startswith("tr") and len(key) >= 3 and key[-1] in PAD_KEYS:
            tempo_reset(PAD_KEYS[key[-1]])

        # reprompt: r1-r8
        elif key[0] == "r" and len(key) >= 2 and key[-1] in PAD_KEYS:
            reprompt(PAD_KEYS[key[-1]])

        # volume: v1-v8
        elif key[0] == "v" and len(key) >= 2 and key[-1] in PAD_KEYS:
            volume(PAD_KEYS[key[-1]])

        # tempo: t1-t8
        elif key[0] == "t" and len(key) >= 2 and key[-1] in PAD_KEYS:
            tempo(PAD_KEYS[key[-1]])

        elif key in PAD_KEYS:
            trigger(PAD_KEYS[key])

        else:
            print(f"  Unknown input '{key}'. Type 's' for status or see help above.")


if __name__ == "__main__":
    main()