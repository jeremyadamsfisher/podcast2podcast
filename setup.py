from setuptools import setup, find_packages


setup(
    name="podcast2podcast",
    version="0.1.0",
    packages=find_packages(include=["podcast2podcast", "podcast2podcast.*"]),
    install_requires=[
        "toml",
        "dynaconf",
        "tqdm",
        "loguru",
        "typer[all]",
        "rich",
        "shellingham",
        "spacy",
        "openai",
        "pydub",
        "google-cloud-texttospeech",
        "whisper @ git+https://github.com/openai/whisper.git#egg=whisper",
    ],
)
