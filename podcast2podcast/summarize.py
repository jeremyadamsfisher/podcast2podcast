from pprint import pformat
from typing import List

import openai
import spacy
import toml
from loguru import logger

from podcast2podcast.config import settings
from podcast2podcast.utils import retry

try:
    import importlib.resources as importlib_resources
except ModuleNotFoundError:
    import importlib_resources

from . import data


class DotDict:
    def __init__(self, d):
        self.__dict__.update(d)


with importlib_resources.open_text(data, "prompt_templates.toml") as f:
    prompt_templates = DotDict(toml.load(f))


def summarize_pipeline(
    transcript: str, podcast: str, episode_name: str, page=100
) -> str:
    """Create a new dialog transcript from a podcast transcript.

    Args:
        transcript (str): The transcript of the podcast episode.
        podcast (str): The name of the podcast.
        episode_name (str): The name of the episode.

    Returns:
        NewPodcastDialogTranscript: The new dialog transcript."""
    openai.api_key = settings.openai_token
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(transcript)
    sents = [s.text.strip() for s in doc.sents]

    logger.debug("transcription: {}", pformat(sents))

    snippets = [" ".join(sents[i : i + page]) for i in range(0, len(sents), page)]
    summaries = [summarize_snippet(snippet) for snippet in snippets]
    logger.debug("summaries: {}", pformat(summaries))

    metasummary = summarize_summaries(summaries)
    logger.debug("metasummary: {}", metasummary)

    metasummary = remove_sponsers(metasummary)
    logger.debug("metasummary without sponsers: {}", metasummary)

    transcript = create_new_podcast_dialog(metasummary, podcast, episode_name)
    logger.debug("new podcast dialog: {}", transcript)

    return transcript


@retry(n=3)
def text_complete(
    prompt: str,
    model="text-davinci-003",
    output_prefix="",
    max_tokens=256,
):
    """Complete text using OpenAI API.

    Args:
        prompt (str): Prompt to complete.
        model (str, optional): Model to use. Defaults to "text-davinci-003".
        output_prefix (str, optional): Prefix to add to the output. Defaults to "".

    Returns:
        str: Completed text, not including the prompt.
    """
    response = openai.Completion.create(
        prompt=prompt + output_prefix,
        model=model,
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    completion = output_prefix + response.choices[0]["text"].strip()
    return completion


def summarize_snippet(snippet: str) -> str:
    """Summarize a snippet of the podcast."""
    prompt = prompt_templates.summarize_snippet.format(snippet=snippet)
    return text_complete(prompt)


def summarize_summaries(summaries: List[str]) -> str:
    """Summarize a list of summaries."""
    prompt = prompt_templates.summarize_summaries.format(
        summaries="\n".join(f" - {summary}" for summary in summaries),
    )
    return text_complete(prompt)


def remove_sponsers(summary: str) -> str:
    """Remove sponsers from a summary."""
    prompt = prompt_templates.remove_sponsers_from_summary.format(summary=summary)
    return text_complete(prompt)


def create_new_podcast_dialog(summary: str, podcast: str, episode_name: str) -> str:
    """Create a new podcast dialog from a summary."""
    first_line = prompt_templates.rewrite_as_a_podcast_transcript_first_line.format(
        podcast=podcast, episode_name=episode_name
    )
    prompt = prompt_templates.rewrite_as_a_podcast_transcript.format(
        podcast=podcast, summary=summary, episode_name=episode_name
    )
    return text_complete(prompt, output_prefix=first_line, max_tokens=1000)
