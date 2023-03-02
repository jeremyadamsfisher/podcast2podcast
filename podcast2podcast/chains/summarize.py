from langchain import LLMChain, OpenAI, PromptTemplate

SUMMARIZE_TEMPLATE_STR = """\
Please summarize the following podcast description. Only include \
information about the content of the episode. For example, ignore links \
to the podcast's website, social media accounts and background reading.

It is CRUCIAL to end your summary with the sentence: Thus concludes \
summary of the podcast.

Here is the description:

```
{description}
```

Begin!

Summary:\
"""

summarize_chain = LLMChain(
    llm=OpenAI(
        temperature=0.0,
        model_kwargs={"stop": ["Thus concludes the summary of the podcast."]},
    ),
    prompt=PromptTemplate(
        input_variables=["description"],
        template=SUMMARIZE_TEMPLATE_STR,
    ),
)


def generate_summary(description: str) -> str:
    """Summarize a podcast description.

    Args:
        description (str): The podcast description.

    Returns:
        str: The summary.

    """
    return summarize_chain.predict(description=description).strip()
