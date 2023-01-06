from typing import Literal

import torchaudio


def text2speech_pipeline(
    transcript: str,
    fp_out="./podcast.mp3",
    preset: Literal["ultra_fast", "fast", "standard", "high_quality"] = "high_quality",
):
    """Convert a transcript to speech.

    Args:
        transcript (str): Transcript.
        fp_out (str, optional): Path to output audio file. Defaults to "./podcast.mp3".
        preset (str, optional): TTS preset. Defaults to "high_quality".

    Returns:
        str: Path to output audio file.

    """
    from tortoise.api import TextToSpeech
    from tortoise.utils.audio import load_voice

    tts = TextToSpeech()
    mouse_voice_samples, mouse_conditioning_latents = load_voice("mouse")
    speech = tts.tts_with_preset(
        voice_samples=mouse_voice_samples,
        conditioning_latents=mouse_conditioning_latents,
    )(transcript, preset=preset)
    torchaudio.save(fp_out, speech.squeeze(0).cpu(), 24000)

    return fp_out
