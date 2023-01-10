from tempfile import NamedTemporaryFile
from typing import Literal

import torchaudio
from pydub import AudioSegment

from podcast2podcast.nlp import nlp


def text2speech_pipeline(
    transcript: str,
    preset: Literal["ultra_fast", "fast", "standard", "high_quality"] = "high_quality",
) -> AudioSegment:
    """Convert a transcript to speech.

    Args:
        transcript (str): Transcript.
        preset (str, optional): TTS preset. Defaults to "high_quality".

    Returns:
        AudioSegment: Audio of podcast episode.

    """
    from tortoise.api import TextToSpeech
    from tortoise.utils.audio import load_voice

    tts = TextToSpeech()
    mouse_voice_samples, mouse_conditioning_latents = load_voice("train_mouse")

    segments = []
    for sentence in nlp(transcript).sents:
        try:
            speech = tts.tts_with_preset(
                sentence.strip(),
                preset=preset,
                voice_samples=mouse_voice_samples,
                conditioning_latents=mouse_conditioning_latents,
            )
        except AssertionError:
            raise ValueError("Tortoise cannot deal with long texts.")
        else:
            with NamedTemporaryFile(suffix=".wav") as t:
                torchaudio.save(t.name, speech.squeeze(0).cpu(), 24000)
                segment = AudioSegment.from_wav(t.name)
                segments.append(segment)

    audio = sum(segments)

    return audio
