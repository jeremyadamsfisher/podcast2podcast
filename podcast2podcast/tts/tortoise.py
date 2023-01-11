import math
import re
from tempfile import NamedTemporaryFile
from typing import Callable, List, Literal

import torchaudio
from pydub import AudioSegment

from podcast2podcast.nlp import nlp


def chunk_texts_into_reasonable_sizes(
    texts: List[str], len_acceptable_callable: Callable
) -> List[str]:
    """Split texts into reasonable sizes.

    Examples:
        >>> texts = ["This is a very long text, and it is too long for the TTS to handle."]
        >>> chunk_texts_into_reasonable_sizes(texts, lambda s: 4 < len(s.split(" ")))
        ["This is a very long text,", "and it is too long for the TTS to handle."]

    Args:
        texts (List[str]): List of texts.
        len_acceptable_callable (Callable): Callable that returns True if the length of the text is acceptable.

    Returns:
        List[str]: List of texts of reasonable size.
    """
    texts_ = []
    check_again = False
    for text in texts:
        if len_acceptable_callable(text):
            texts_.append(text)
        else:
            check_again = True
            m = [t for t in re.split(r"(,|;)", text) if t]
            split_idx = math.ceil((len(m) + 1) / 2)
            left, right = "".join(m[:split_idx]).strip(), "".join(m[split_idx:]).strip()

            # ensure that the split is not too aggressive
            if len(left) <= 1 or len(right) <= 1:
                texts_.append(text)
            else:
                texts_.extend([left, right])

    # splitting occured or splitting occured and had no effect
    if check_again is False or texts_ == texts:
        return texts_

    return chunk_texts_into_reasonable_sizes(texts_, len_acceptable_callable)


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

    text_segments = [sent.text for sent in nlp(transcript).sents]
    text_segments = chunk_texts_into_reasonable_sizes(
        text_segments, lambda s: 20 < len(s.split(" "))
    )

    audio_segments = []
    for sentence in text_segments:
        try:
            speech = tts.tts_with_preset(
                sentence.text.strip(),
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
                audio_segments.append(segment)

    audio = sum(audio_segments)

    return audio
