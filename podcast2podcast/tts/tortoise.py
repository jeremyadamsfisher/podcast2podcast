import abc
from tempfile import NamedTemporaryFile
from typing import Literal, Optional

import spacy
import torchaudio
from loguru import logger
from pydub import AudioSegment

nlp = spacy.load("en_core_web_sm")


def break_up_long_sentence(sent: str):
    """Split texts into reasonable sizes.

    Args:
        sent (str): A potentially long sentence.

    Examples:
        >>> break_up_long_sentence(
        >>>     "It was the best of times, it was the worst of times, it was the age of wisdom, "
        >>>     "it was the age of foolishness, it was the epoch of belief, it was the epoch of "
        >>>     "incredulity, it was the season of light, it was the season of darkness, it was "
        >>>     "the spring of hope, it was the winter of despair."
        >>> )
        ["It was the best of times, it was the worst of times, it was the age of wisdom,",
         "it was the age of foolishness, it was the epoch of belief,",
         "it was the epoch of incredulity, it was the season of light, it was the season of darkness,",
         "it was the spring of hope, it was the winter of despair."]

    Returns:
        List[str]: List of clauses or a sentence of a reasonable size.

    """
    if sent.count(" ") < 25 or sent.count(",") == 0:
        return [sent.strip()]
    clauses = sent.split(",")
    left = ",".join(clauses[: len(clauses) // 2]).strip() + ","
    right = ",".join(clauses[len(clauses) // 2 :]).strip()
    return sum((break_up_long_sentence(s) for s in (left, right)), [])


class TTSCache(abc.ABC):
    """Cache for TTS methods."""

    def __getitem__(self, item):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError


def tts_gen(
    transcript: str, preset: str, cache: Optional[TTSCache] = None
) -> AudioSegment:
    # importing here to avoid doing so if using WaveNet
    from tortoise.api import TextToSpeech
    from tortoise.utils.audio import load_voice

    tts = TextToSpeech()
    mouse_voice_samples, mouse_conditioning_latents = load_voice("train_mouse")

    for sentence in nlp(transcript).sents:
        for chunk in break_up_long_sentence(sentence.text):
            logger.info("running tts on: {}", chunk)
            try:
                assert cache is not None
                segment = cache[chunk]
            except (KeyError, AssertionError):
                try:
                    speech = tts.tts_with_preset(
                        chunk,
                        preset=preset,
                        voice_samples=mouse_voice_samples,
                        conditioning_latents=mouse_conditioning_latents,
                    )
                except AssertionError:
                    raise ValueError("Tortoise cannot deal with long texts.")
                with NamedTemporaryFile(suffix=".wav") as t:
                    torchaudio.save(t.name, speech.squeeze(0).cpu(), 24000)
                    segment = AudioSegment.from_wav(t.name)
            yield segment


def tts(
    transcript,
    preset: Literal["ultra_fast", "fast", "standard", "high_quality"] = "high_quality",
):
    """Convert a transcript to speech.

    Args:
        transcript (str): Transcript.
        preset (str, optional): TTS preset. Defaults to "high_quality".

    Returns:
        AudioSegment: Audio of podcast episode.

    """
    audio_segments = []
    for segment in tts_gen(transcript, preset):
        audio_segments.append(segment)
    return sum(audio_segments)
