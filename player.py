# player.py
# Handles all audio playback using sounddevice + soundfile + librosa.
# Supports multiple simultaneous looping pads on independent threads.
# Each pad gets its own thread so starting/stopping one never affects others.
# Supports per-pad volume and per-pad tempo (time-stretching via librosa).

import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
import librosa
from audio_gen import get_cache_path

# ----------------------------------------------------------------
# Global state
# ----------------------------------------------------------------

# Active playback threads: { pad_id: { "stop_event": Event, "thread": Thread } }
_active_pads: dict = {}

# Per-pad volume levels: { pad_id: float (0.0 - 1.0) }
_volumes: dict = {}

# Per-pad tempo rates: { pad_id: float (0.25 - 4.0) } — 1.0 = normal speed
_tempo_rates: dict = {}

_lock = threading.Lock()


# ----------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------

def _get_volume(pad_id: str) -> float:
    with _lock:
        return _volumes.get(pad_id, 1.0)


def _get_tempo(pad_id: str) -> float:
    with _lock:
        return _tempo_rates.get(pad_id, 1.0)


def _load_audio(pad_id: str) -> tuple[np.ndarray, int] | tuple[None, None]:
    """Load and time-stretch audio for a pad based on its tempo rate."""
    cache_path = get_cache_path(pad_id)
    try:
        data, samplerate = sf.read(cache_path, dtype="float32", always_2d=True)
    except Exception as e:
        print(f"[Player] ✗ Could not read audio for '{pad_id}': {e}")
        return None, None

    rate = _get_tempo(pad_id)
    if rate != 1.0:
        # librosa works on mono, process each channel separately
        stretched_channels = []
        for ch in range(data.shape[1]):
            stretched = librosa.effects.time_stretch(data[:, ch], rate=rate)
            stretched_channels.append(stretched)
        data = np.stack(stretched_channels, axis=1)

    return data, samplerate


def _loop_audio(pad_id: str, stop_event: threading.Event):
    """
    Internal thread target. Loads audio, applies tempo stretch, then loops
    it continuously applying per-pad volume until stop_event is set.
    """
    data, samplerate = _load_audio(pad_id)
    if data is None:
        return

    tempo = _get_tempo(pad_id)
    tempo_str = f" @ {tempo:.2f}x" if tempo != 1.0 else ""
    print(f"[Player] ▶ Looping '{pad_id}'{tempo_str}")

    with sd.OutputStream(samplerate=samplerate, channels=data.shape[1]) as stream:
        while not stop_event.is_set():
            volume = _get_volume(pad_id)
            stream.write(data * volume)

    print(f"[Player] ■ Stopped '{pad_id}'")


# ----------------------------------------------------------------
# Public API
# ----------------------------------------------------------------

def play(pad_id: str):
    """Start looping a pad. If already playing, do nothing."""
    with _lock:
        if pad_id in _active_pads:
            print(f"[Player] '{pad_id}' is already playing.")
            return

    stop_event = threading.Event()
    thread = threading.Thread(
        target=_loop_audio,
        args=(pad_id, stop_event),
        daemon=True,
        name=f"pad-{pad_id}"
    )
    with _lock:
        _active_pads[pad_id] = {"stop_event": stop_event, "thread": thread}
    thread.start()


def stop(pad_id: str):
    """Stop a looping pad. If not playing, do nothing."""
    with _lock:
        entry = _active_pads.pop(pad_id, None)

    if entry:
        entry["stop_event"].set()
        entry["thread"].join(timeout=2)
        print(f"[Player] ■ '{pad_id}' stopped cleanly.")
    else:
        print(f"[Player] '{pad_id}' was not playing.")


def toggle(pad_id: str) -> bool:
    """Toggle a pad on or off. Returns True if now playing, False if stopped."""
    with _lock:
        is_on = pad_id in _active_pads

    if is_on:
        stop(pad_id)
        return False
    else:
        play(pad_id)
        return True


def stop_all():
    """Stop every currently playing pad."""
    with _lock:
        pad_ids = list(_active_pads.keys())
    for pad_id in pad_ids:
        stop(pad_id)


def is_playing(pad_id: str) -> bool:
    """Return True if a pad is currently looping."""
    with _lock:
        return pad_id in _active_pads


def set_volume(pad_id: str, level: float):
    """
    Set per-pad volume. Level should be between 0.0 (silent) and 1.0 (full).
    Takes effect immediately on the next audio buffer write.
    """
    level = max(0.0, min(1.0, level))  # clamp to valid range
    with _lock:
        _volumes[pad_id] = level
    print(f"[Player] Volume '{pad_id}' → {level:.2f}")


def get_volume(pad_id: str) -> float:
    """Return current volume for a pad (default 1.0)."""
    return _get_volume(pad_id)


def set_tempo(pad_id: str, rate: float):
    """
    Set tempo rate for a specific pad. 1.0 = normal, 2.0 = double speed, 0.5 = half speed.
    If the pad is currently playing, it will restart with the new rate applied.
    
    Args:
        pad_id: The pad to adjust
        rate: Tempo multiplier (0.25 - 4.0)
    """
    rate = max(0.25, min(4.0, rate))  # clamp to sane range

    with _lock:
        _tempo_rates[pad_id] = rate

    print(f"[Player] Tempo '{pad_id}' → {rate:.2f}x")

    # Restart the pad if it's playing so it picks up the new stretch
    with _lock:
        is_active = pad_id in _active_pads
    
    if is_active:
        stop(pad_id)
        play(pad_id)


def get_tempo(pad_id: str) -> float:
    """Return current tempo rate for a pad (default 1.0)."""
    return _get_tempo(pad_id)


def set_all_tempos(rate: float):
    """
    Set the same tempo rate for ALL pads (convenience function).
    Currently playing pads will restart with the new rate.
    
    Args:
        rate: Tempo multiplier (0.25 - 4.0) to apply to all pads
    """
    rate = max(0.25, min(4.0, rate))
    
    # Get all pad IDs from active pads and tempo dict
    with _lock:
        all_pad_ids = set(_active_pads.keys()) | set(_tempo_rates.keys())
    
    # Set tempo for each pad
    for pad_id in all_pad_ids:
        set_tempo(pad_id, rate)
    
    print(f"[Player] Set all pad tempos to {rate:.2f}x")


def reset_tempo(pad_id: str):
    """Reset a pad's tempo to 1.0 (normal speed)."""
    set_tempo(pad_id, 1.0)


def reset_all_tempos():
    """Reset all pads to normal tempo (1.0x)."""
    set_all_tempos(1.0)