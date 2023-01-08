from tempfile import NamedTemporaryFile
from typing import Literal, Tuple

import torchaudio
from loguru import logger
from pydub import AudioSegment

from podcast2podcast.nlp import nlp


def split_transcript(transcript: str) -> Tuple[str, str]:
    """Split a transcript into two parts.

    Args:
        transcript (str): Transcript.

    Returns:
        Tuple[str, str]: First and second half of transcript.
    """
    doc = nlp(transcript)
    sents = [s.text.strip() for s in doc.sents]
    return " ".join(sents[: len(sents) // 2]), " ".join(sents[len(sents) // 2 :])


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
    try:
        speech = tts.tts_with_preset(
            transcript,
            preset=preset,
            voice_samples=mouse_voice_samples,
            conditioning_latents=mouse_conditioning_latents,
        )
    except AssertionError:
        logger.warning(
            "Tortoise cannot deal with very long texts. Rerunning tortoise on "
            "smaller segments of the text and concatenating the results."
        )
        first_half, second_half = split_transcript(transcript)
        return text2speech_pipeline(first_half) + text2speech_pipeline(second_half)

    with NamedTemporaryFile(suffix=".wav") as t:
        torchaudio.save(t.name, speech.squeeze(0).cpu(), 24000)
        audio = AudioSegment.from_wav(t.name)

    return audio
