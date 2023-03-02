from typing import TYPE_CHECKING, Literal, Union

from podcast2podcast.dialog import new_dialog
from podcast2podcast.rss import get_podcast_details
from podcast2podcast.tts.google import tts as google_tts
from podcast2podcast.tts.tortoise import tts as tortoise_tts
from podcast2podcast.utils import yap

if TYPE_CHECKING:
    from pydub import AudioSegment


def pipeline(
    url,
    episode_idx,
    tts_method: Literal["google", "tortoise", None] = "tortoise",
) -> Union[str, "AudioSegment"]:
    """Run the entire pipeline (transcription to spoken output).

    Args:
        url (str): URL to audio file.
        episode_idx (int): Episode index within RSS feed.
        tts_method(str, optional): Text-to-speech method. Defaults to "google".
            If None, skip TTS.

    Returns:
        AudioSegment: Audio of podcast episode.

    """

    with yap(about="getting podcast information"):
        details = get_podcast_details(url, episode_idx)

    with yap(about="creating new dialog"):
        transcript = new_dialog(*details)

    if tts_method is None:
        return transcript

    with yap(about="generating audio"):
        if tts_method == "google":
            audio = google_tts(transcript)
        elif tts_method == "tortoise":
            audio = tortoise_tts(transcript, preset="high_quality")
        else:
            raise ValueError(tts_method)
    return audio
