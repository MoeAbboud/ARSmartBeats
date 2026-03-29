# audio_gen.py (enhanced version)
# Add retry logic and better error handling for production use

import os
import requests
import time
from typing import Tuple, Optional

ELEVENLABS_URL = "https://api.elevenlabs.io/v1/sound-generation"
AUDIO_CACHE_DIR = "audio_cache"
AUDIO_FORMAT = "mp3_44100_128"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def ensure_cache_dir():
    """Create the audio_cache/ folder if it doesn't exist."""
    os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)


def get_cache_path(pad_id: str) -> str:
    """Return the local file path for a pad's cached audio file."""
    return os.path.join(AUDIO_CACHE_DIR, f"{pad_id}.mp3")


def generate_sound(pad_id: str, prompt: str, retry_count: int = 0) -> Tuple[bool, str]:
    """
    Call the ElevenLabs SFX API to generate audio for a pad with retry logic.

    Args:
        pad_id:  The pad's unique ID (e.g. "kick")
        prompt:  The text description sent to ElevenLabs
        retry_count: Current retry attempt (internal)

    Returns:
        (success: bool, message: str)
    """
    ensure_cache_dir()

    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        print(f"[ElevenLabs] ✗ No API key found. Check your .env file.")
        return False, "Missing ELEVENLABS_API_KEY"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "text": prompt,
        "model_id": "eleven_text_to_sound_v2",
        "duration_seconds": None,
        "prompt_influence": 0.5,
        "output_format": AUDIO_FORMAT,
    }

    try:
        retry_msg = f" (attempt {retry_count + 1}/{MAX_RETRIES})" if retry_count > 0 else ""
        print(f"[ElevenLabs] Generating '{pad_id}'{retry_msg}: {prompt[:60]}...")
        
        response = requests.post(ELEVENLABS_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            cache_path = get_cache_path(pad_id)
            with open(cache_path, "wb") as f:
                f.write(response.content)
            print(f"[ElevenLabs] ✓ Saved {pad_id} → {cache_path}")
            return True, cache_path

        elif response.status_code == 429:  # Rate limit
            if retry_count < MAX_RETRIES:
                wait_time = RETRY_DELAY * (retry_count + 1)
                print(f"[ElevenLabs] ⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                return generate_sound(pad_id, prompt, retry_count + 1)
            else:
                return False, "Rate limit exceeded after retries"

        else:
            error_msg = f"API error {response.status_code}: {response.text}"
            print(f"[ElevenLabs] ✗ {pad_id} failed — {error_msg}")
            
            if retry_count < MAX_RETRIES and response.status_code >= 500:
                print(f"[ElevenLabs] ⏳ Server error, retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
                return generate_sound(pad_id, prompt, retry_count + 1)
            
            return False, error_msg

    except requests.exceptions.Timeout:
        msg = "Request timed out after 30s"
        print(f"[ElevenLabs] ✗ {pad_id} — {msg}")
        
        if retry_count < MAX_RETRIES:
            print(f"[ElevenLabs] ⏳ Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
            return generate_sound(pad_id, prompt, retry_count + 1)
        
        return False, msg

    except Exception as e:
        msg = str(e)
        print(f"[ElevenLabs] ✗ {pad_id} — Unexpected error: {msg}")
        return False, msg


def is_cached(pad_id: str) -> bool:
    """Return True if this pad already has a cached audio file."""
    return os.path.exists(get_cache_path(pad_id))


def clear_cache(pad_id: Optional[str] = None):
    """
    Clear cached audio files.
    
    Args:
        pad_id: If provided, clear only this pad. Otherwise clear all.
    """
    if pad_id:
        cache_path = get_cache_path(pad_id)
        if os.path.exists(cache_path):
            os.remove(cache_path)
            print(f"[Cache] Cleared {pad_id}")
    else:
        ensure_cache_dir()
        for filename in os.listdir(AUDIO_CACHE_DIR):
            if filename.endswith('.mp3'):
                os.remove(os.path.join(AUDIO_CACHE_DIR, filename))
        print(f"[Cache] Cleared all cached audio")