from langchain import LLMChain, OpenAI, PromptTemplate

END = "Thus concludes summary of the podcast."

SUMMARIZE_TEMPLATE_STR = """\
Please summarize the following podcast description. Only include \
information about the content of the episode. For example, ignore links \
to the podcast's website, social media accounts and background reading.

It is CRUCIAL to end your summary with the sentence: {end}

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
        model_kwargs={"stop": [END]},
    ),
    prompt=PromptTemplate(
        input_variables=["description", "end"],
        template=SUMMARIZE_TEMPLATE_STR,
    ).partial(end=END),
)


def generate_summary(description: str) -> str:
    """Summarize a podcast description.

    Args:
        description (str): The podcast description.

    Returns:
        str: The summary.

    """
    return summarize_chain.predict(description=description).strip()
