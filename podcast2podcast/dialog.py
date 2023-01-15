import re

import openai
import toml

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
    prompts = DotDict(toml.load(f))


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
    summary = text_complete(prompts.summarize(description=description))
    first_line = prompts.first_line.format(podcast_title, episode_title)
    return text_complete(
        prompts.rewrite(summary=summary, podcast_title=podcast_title) + first_line,
    )


@retry(n=3)
def text_complete(
    prompt: str,
    model="text-davinci-003",
    output_prefix="",
    max_tokens=256,
    json_capture=True,
):
    """Complete text using OpenAI API.

    Args:
        prompt (str): Prompt to complete.
        model (str, optional): Model to use. Defaults to "text-davinci-003".
        output_prefix (str, optional): Prefix to add to the output. Defaults to "".
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 256.
        json_capture (bool, optional): Whether to parse outputs as a JSON. Defaults to True.

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
    if json_capture:
        try:
            (completion,) = re.findall(r"^(.*?)\"}", completion, re.DOTALL)
        except TypeError:
            raise ValueError(f"Invalid JSON: {completion}")
    return completion
