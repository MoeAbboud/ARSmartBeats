# server.py
# Flask backend — exposes REST endpoints that LightGuide will call on pad touch.
# Run this first before launching LightGuide.
#
# Endpoints:
#   POST /pad/trigger     — toggle a pad loop on/off
#   POST /pad/reprompt    — regenerate a pad's audio with a new prompt
#   POST /pad/volume      — set per-pad volume (0.0 - 1.0)
#   POST /pad/tempo       — set per-pad tempo rate (0.25 - 4.0)
#   POST /tempo/all       — set tempo for ALL pads at once
#   GET  /pad/status      — return full state of all pads

import time
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from pads_config import PADS, PADS_BY_ID
from audio_gen import generate_sound, is_cached
from player import (
    toggle, stop, is_playing, 
    set_volume, get_volume, 
    set_tempo, get_tempo,
    set_all_tempos, reset_tempo, reset_all_tempos
)

load_dotenv()

app = Flask(__name__)

_regenerating: dict = {}
_regen_lock = threading.Lock()


# ----------------------------------------------------------------
# STARTUP — pre-generate all pad sounds in batches of 4
# ----------------------------------------------------------------

def _pregenerate_all():
    print("\n[Startup] Pre-generating all pad sounds (in batches of 4)...\n")

    pads_to_generate = [pad for pad in PADS if not is_cached(pad["id"])]

    if not pads_to_generate:
        print("[Startup] All pads already cached, skipping generation.\n")
        return

    batch_size = 4
    for i in range(0, len(pads_to_generate), batch_size):
        batch = pads_to_generate[i:i + batch_size]
        threads = []
        for pad in batch:
            t = threading.Thread(
                target=generate_sound,
                args=(pad["id"], pad["prompt"]),
                daemon=True,
                name=f"pregen-{pad['id']}"
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        if i + batch_size < len(pads_to_generate):
            print("[Startup] Batch done, waiting 2s before next batch...")
            time.sleep(2)

    print("\n[Startup] All pads ready.\n")


# ----------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------

@app.route("/pad/trigger", methods=["POST"])
def pad_trigger():
    """Toggle a pad loop on/off."""
    data = request.get_json()
    pad_id = data.get("pad_id")

    if not pad_id or pad_id not in PADS_BY_ID:
        return jsonify({"error": f"Unknown pad_id: '{pad_id}'"}), 400

    with _regen_lock:
        if _regenerating.get(pad_id):
            return jsonify({"error": f"Pad '{pad_id}' is currently regenerating."}), 409

    if not is_cached(pad_id):
        return jsonify({"error": f"Pad '{pad_id}' has no audio yet."}), 503

    now_playing = toggle(pad_id)
    return jsonify({"pad_id": pad_id, "playing": now_playing})


@app.route("/pad/reprompt", methods=["POST"])
def pad_reprompt():
    """Regenerate a pad's audio with a new prompt."""
    data = request.get_json()
    pad_id = data.get("pad_id")
    new_prompt = data.get("prompt", "").strip()

    if not pad_id or pad_id not in PADS_BY_ID:
        return jsonify({"error": f"Unknown pad_id: '{pad_id}'"}), 400

    if not new_prompt:
        return jsonify({"error": "A 'prompt' field is required."}), 400

    with _regen_lock:
        if _regenerating.get(pad_id):
            return jsonify({"error": f"Pad '{pad_id}' is already regenerating."}), 409
        _regenerating[pad_id] = True

    if is_playing(pad_id):
        stop(pad_id)

    PADS_BY_ID[pad_id]["prompt"] = new_prompt

    def _regen_thread():
        try:
            success, message = generate_sound(pad_id, new_prompt)
            if success:
                print(f"[Reprompt] ✓ '{pad_id}' ready with new sound.")
            else:
                print(f"[Reprompt] ✗ '{pad_id}' failed: {message}")
        finally:
            with _regen_lock:
                _regenerating[pad_id] = False

    threading.Thread(target=_regen_thread, daemon=True, name=f"regen-{pad_id}").start()
    return jsonify({"pad_id": pad_id, "status": "regenerating"})


@app.route("/pad/volume", methods=["POST"])
def pad_volume():
    """
    Set per-pad volume.

    Expected JSON body:
        { "pad_id": "kick", "volume": 0.8 }

    Volume must be between 0.0 (silent) and 1.0 (full).
    Takes effect immediately — no need to restart the pad.
    """
    data = request.get_json()
    pad_id = data.get("pad_id")
    volume = data.get("volume")

    if not pad_id or pad_id not in PADS_BY_ID:
        return jsonify({"error": f"Unknown pad_id: '{pad_id}'"}), 400

    if volume is None or not isinstance(volume, (int, float)):
        return jsonify({"error": "'volume' must be a number between 0.0 and 1.0"}), 400

    set_volume(pad_id, float(volume))
    return jsonify({"pad_id": pad_id, "volume": get_volume(pad_id)})


@app.route("/pad/tempo", methods=["POST"])
def pad_tempo():
    """
    Set tempo rate for a specific pad (time-stretches that pad's audio).

    Expected JSON body:
        { "pad_id": "kick", "rate": 1.5 }

    Rate range: 0.25 (quarter speed) to 4.0 (quadruple speed). 1.0 = normal.
    If the pad is currently playing, it will restart with the new rate.
    """
    data = request.get_json()
    pad_id = data.get("pad_id")
    rate = data.get("rate")

    if not pad_id or pad_id not in PADS_BY_ID:
        return jsonify({"error": f"Unknown pad_id: '{pad_id}'"}), 400

    if rate is None or not isinstance(rate, (int, float)):
        return jsonify({"error": "'rate' must be a number between 0.25 and 4.0"}), 400

    set_tempo(pad_id, float(rate))
    return jsonify({"pad_id": pad_id, "tempo_rate": get_tempo(pad_id)})


@app.route("/tempo/all", methods=["POST"])
def tempo_all():
    """
    Set the same tempo rate for ALL pads at once.

    Expected JSON body:
        { "rate": 1.5 }

    Rate range: 0.25 to 4.0. Currently playing pads will restart.
    """
    data = request.get_json()
    rate = data.get("rate")

    if rate is None or not isinstance(rate, (int, float)):
        return jsonify({"error": "'rate' must be a number between 0.25 and 4.0"}), 400

    set_all_tempos(float(rate))
    return jsonify({"tempo_rate": float(rate), "applied_to": "all_pads"})


@app.route("/tempo/reset", methods=["POST"])
def tempo_reset():
    """
    Reset tempo for one pad or all pads to 1.0 (normal speed).

    Expected JSON body:
        { "pad_id": "kick" }  — reset one pad
        { }                   — reset all pads (omit pad_id)
    """
    data = request.get_json()
    pad_id = data.get("pad_id")

    if pad_id:
        if pad_id not in PADS_BY_ID:
            return jsonify({"error": f"Unknown pad_id: '{pad_id}'"}), 400
        reset_tempo(pad_id)
        return jsonify({"pad_id": pad_id, "tempo_rate": 1.0})
    else:
        reset_all_tempos()
        return jsonify({"tempo_rate": 1.0, "applied_to": "all_pads"})


@app.route("/pad/status", methods=["GET"])
def pad_status():
    """Return full state of all pads (no more global tempo)."""
    with _regen_lock:
        regen_snapshot = dict(_regenerating)

    status = []
    for pad in PADS:
        pid = pad["id"]
        status.append({
            "id": pid,
            "label": pad["label"],
            "color": pad["color"],
            "prompt": pad["prompt"],
            "playing": is_playing(pid),
            "regenerating": regen_snapshot.get(pid, False),
            "ready": is_cached(pid),
            "volume": get_volume(pid),
            "tempo_rate": get_tempo(pid),
        })

    return jsonify({"pads": status})


# ----------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------

if __name__ == "__main__":
    _pregenerate_all()
    print("[Server] Starting Flask on http://0.0.0.0:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)