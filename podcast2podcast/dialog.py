import re

import openai

from podcast2podcast.config import settings
from podcast2podcast.utils import retry

SUMMARIZE = """\
The following is the description of a podcast episode. 

Description: {}

Please write a concise summary of this podcast as a JSON.

{{"summary": "\
"""

REWRITE = """\
The following JSON is a summary of a podcast called "{}"

Summary: {}

Please write the dialog for a talk show that discusses this podcast. The host of the podcast is "Jeremy-Bot." Respond with JSON. Make sure to end with the tagline: "That's all for today. Join us next time for another exciting summary"

{{"dialog": "\
"""

FIRST_LINE = """\
Welcome back. I'm Jeremy-Bot, an artificial intelligence that summarizes \
podcasts. Today we are summarizing {}: {}.\
"""


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
    summary = text_complete(SUMMARIZE.format(description))
    return text_complete(
        REWRITE.format(podcast_title, summary),
        output_prefix=FIRST_LINE.format(podcast_title, episode_title),
    )


@retry(n=3)
def text_complete(
    prompt: str,
    model="text-davinci-003",
    max_tokens=256,
    json_capture=True,
    output_prefix="",
):
    """Complete text using OpenAI API.

    Args:
        prompt (str): Prompt to complete.
        model (str, optional): Model to use. Defaults to "text-davinci-003".
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 256.
        json_capture (bool, optional): Whether to parse outputs as a JSON. Defaults to True.
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
    if json_capture:
        try:
            (completion,) = re.findall(r"^(.*?)\"}", completion, re.DOTALL)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid JSON: {completion}")
    return completion
