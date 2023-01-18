import json
import re
from typing import Callable, Optional

import openai
from loguru import logger

from podcast2podcast.config import settings
from podcast2podcast.utils import retry

SUMMARIZE = """\
The following is the description of a podcast episode. 

Description: {}

Please write a concise summary of this podcast as a JSON.
"""

REWRITE = """\
The following JSON is a summary of a podcast called "{}"

Summary: {}

Please write the dialog for a talk show that discusses this podcast. The host of the podcast is "Jeremy-Bot." There are no other guests. Respond with JSON with the key "dialog". Make sure to end with the tagline: "That's all for today. Join us next time for another exciting summary"\
"""

FIRST_LINE = """\
Welcome back. I'm Jeremy-Bot, an artificial intelligence that summarizes \
podcasts. Today we are summarizing {}: {}.\
"""


def attempt_to_salvage_dialog_that_is_slightly_too_long(dialog):
    pat = r"(that'?s all for today.*$)"
    if re.findall(pat, dialog, flags=re.IGNORECASE):
        return re.sub(
            pat,
            "That's all for today. Join us next time for another exciting summary.\"}",
            dialog,
            flags=re.IGNORECASE,
        )
    else:
        raise ValueError(f"Can't salvage dialog that is too long: `{dialog}`")


def new_dialog(podcast_title, episode_title, description) -> str:
    """Create a new dialog transcript from a podcast transcript.

    Args:
        podcast_title (str): The podcast title.
        episode_title (str): The episode title.
        description (str): The episode description.

    Returns:
        str: The new dialog transcript.

    """
    openai.api_key = settings.openai_token
    summary = json_complete(prompt=SUMMARIZE.format(description), key="summary")
    return json_complete(
        prompt=REWRITE.format(podcast_title, summary),
        output_prefix=FIRST_LINE.format(podcast_title, episode_title),
        key="dialog",
        attempt_fix=attempt_to_salvage_dialog_that_is_slightly_too_long,
    )


def text_complete(
    prompt: str,
    model="text-davinci-003",
    max_tokens=256,
    output_prefix="",
) -> str:
    """Complete text using OpenAI API.

    Args:
        prompt (str): Prompt to complete.
        model (str, optional): Model to use. Defaults to "text-davinci-003".
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 256.
        json_capture (bool, optional): Whether to parse outputs as a JSON. Defaults to False.
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
    return output_prefix + response.choices[0]["text"].strip()


@retry(n=3, delay=10)
def json_complete(
    key: str,
    prompt: str,
    model="text-davinci-003",
    max_tokens=256,
    output_prefix="",
    attempt_fix: Optional[Callable] = None,
) -> str:
    """Complete text using OpenAI API, evoking JSON outputs from the model to
    know what part of the output is relevant.

    Args:
        key (str): Key to extract from JSON from GPT3.
        *args, **kwargs: Arguments to pass to text_complete.

    Returns:
        str: Completed text, not including the prompt.

    """
    json_start = f'{{"{key}": "'  # e.g., '{"summary": "'
    if output_prefix:
        json_start += " " + output_prefix
    completion = text_complete(
        prompt,
        model,
        max_tokens,
        output_prefix=json_start,
    )
    try:
        (completion,) = re.findall(r"^({\".*?\"})", completion, re.DOTALL)
    except ValueError:
        logger.warning(f"Invalid JSON: {completion}. Attempting to fix...")
        completion = attempt_fix(completion)
        try:
            (completion,) = re.findall(r"^({\".*?\"})", completion, re.DOTALL)
        except ValueError:
            raise ValueError(f"Invalid JSON: {completion}")
    try:
        completion = json.loads(completion.replace("\n", r"\n"))[key]
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Invalid JSON: {completion}")
    return completion
