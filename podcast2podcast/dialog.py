from loguru import logger

from podcast2podcast.chains.summarize import generate_summary
from podcast2podcast.chains.transcript import generate_transcript


def new_dialog(podcast_title, episode_title, description) -> str:
    """Create a new dialog transcript from a podcast transcript.

    Args:
        podcast_title (str): The podcast title.
        episode_title (str): The episode title.
        description (str): The episode description.

    Returns:
        str: The new dialog transcript.

    """
    logger.info("Description: {}", description)

    summary = generate_summary(description)
    transcript = generate_transcript(podcast_title, episode_title, summary)

    return transcript
