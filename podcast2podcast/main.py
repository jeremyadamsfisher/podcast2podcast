from typing import Literal

from pydub import AudioSegment

from podcast2podcast.summarize import summarize_pipeline as summarize
from podcast2podcast.transcribe import FIVE_MINUTES
from podcast2podcast.transcribe import transcribe_pipeline as transcribe
from podcast2podcast.tts.google import text2speech_pipeline as google_tts
from podcast2podcast.tts.tortoise import text2speech_pipeline as tortoise_tts
from podcast2podcast.utils import yap


def pipeline(
    url,
    podcast,
    episode_name,
    duration=FIVE_MINUTES,
    tts_method: Literal["google", "tortoise"] = "google",
    whisper_model_size="medium",
) -> AudioSegment:
    """Run the entire pipeline (transcription to spoken output).

    Args:
        url (str): URL to audio file.
        podcast (str): Podcast name.
        episode_name (str): Episode name.
        duration (int, optional): Duration in seconds. Defaults to the first 5 minutes of the episode.
        tts_method(str, optional): Text-to-speech method. Defaults to "google".
        whisper_model_size(str, optional): Model size for the whisper model. Defaults to "medium".

    Returns:
        AudioSegment: Audio of podcast episode.
    """

    with yap(about="transcribing"):
        transcript = transcribe(url, duration, model_size=whisper_model_size)
    with yap(about="creating new dialog"):
        transcript_generated = summarize(transcript, podcast, episode_name)
    with yap(about="generating audio"):
        tts = {"google": google_tts, "tortoise": tortoise_tts}[tts_method]
        audio = tts(transcript_generated)

    return audio
