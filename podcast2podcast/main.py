from typing import TYPE_CHECKING, Literal, Union

from podcast2podcast.dialog import new_dialog
from podcast2podcast.rss import parse_rss
from podcast2podcast.tts.google import tts as google_tts
from podcast2podcast.tts.tortoise import tts as tortoise_tts
from podcast2podcast.utils import yap

if TYPE_CHECKING:
    from pydub import AudioSegment


def pipeline(
    url,
    episode_idx: Union[str, int],
    tts_method: Literal["google", "tortoise", None] = "tortoise",
) -> Union[str, "AudioSegment"]:
    """Run the entire pipeline (transcription to spoken output).

    Args:
        url (str): URL to audio file.
        episode_idx (int | str): Episode index within RSS feed: either the episode number or the episode title.
        tts_method(str, optional): Text-to-speech method. Defaults to "google".
            If None, skip TTS.

    Returns:
        AudioSegment: Audio of podcast episode.

    """

    with yap(about="getting podcast information"):
        podcast_title, episodes = parse_rss(url, episode_idx)
        try:
            assert isinstance(
                episode_idx, int
            ), "episode_idx must be an integer to index on the episode list"
            episode_title, episode_description = episodes[episode_idx]
        except (TypeError, AssertionError):
            assert isinstance(
                episode_idx, str
            ), "episode_idx must be a string search for an episode"
            (episode,) = [e for e in episodes if e.title.lower() == episode_idx.lower()]
            episode_title, episode_description = episode

    with yap(about="creating new dialog"):
        transcript = new_dialog(podcast_title, episode_title, episode_description)

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
