"""Audio utilities for UI presentation layer."""

import io
import wave


def pcm_to_wav(
    pcm_data: bytes,
    sample_rate: int = 24000,
    channels: int = 1,
    sample_width: int = 2,
) -> bytes:
    """Convert raw PCM to WAV for browser playback.

    This is a presentation-layer concern - the API returns raw PCM,
    but browsers require WAV format with headers for playback.

    Args:
        pcm_data: Raw PCM audio bytes.
        sample_rate: Sample rate in Hz (default 24000).
        channels: Number of channels (1 for mono, 2 for stereo).
        sample_width: Bytes per sample (2 for 16-bit, 4 for 32-bit).

    Returns:
        WAV-formatted audio bytes with proper headers.
    """
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)

    buffer.seek(0)
    return buffer.read()


__all__ = ["pcm_to_wav"]
