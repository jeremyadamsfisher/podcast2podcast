from pathlib import Path
from tempfile import NamedTemporaryFile as TempFile
from typing import Literal, Optional
from urllib.parse import urlparse

import whisper
from podcast2podcast.utils import download_file
from pydub import AudioSegment


def trim_audio(fp_in, fp_out, duration, format="wav"):
    """Trim audio to a given duration.

    Args:
        fp_in (str): Path to input audio file.
        fp_out (str): Path to output audio file.
        duration (int): Duration in seconds.
        format (str, optional): Output format. Defaults to "wav".

    """

    suffix = Path(fp_in).suffix.replace(".", "")
    audio = AudioSegment.from_file(fp_in, format=suffix)
    audio[slice(0, duration * 1000)].export(fp_out, format=format)


FIVE_MINUTES = 5 * 60


def transcribe_pipeline(
    url: str,
    duration: Optional[int] = None,
    model_size: Literal["small", "medium", "large", "base"] = "small",
) -> str:
    """Transcribe audio from a given URL.

    Args:
        url (str): URL to audio file.
        duration (int, optional): Duration in seconds. Defaults to the entire length of the episode.
        model_size (str, optional): Model size. Defaults to "small".

    Returns:
        str: Transcription.

    """
    suffix = Path(urlparse(url).path).suffix
    model = whisper.load_model(model_size)
    with TempFile(suffix=suffix) as t_in, TempFile(suffix=suffix) as t_out:
        download_file(url, t_in.name)
        if duration is None:
            audio_fp = t_in.name
        else:
            trim_audio(t_in.name, t_out.name, duration)
            audio_fp = t_out.name
        audio = whisper.load_audio(audio_fp)
    transcription = model.transcribe(
        audio,
        language="english",
        task="transcribe",
    )
    transcript = transcription["text"].strip()
    return transcript
