import sys

from setuptools import find_packages, setup

requirements = [
    "Unidecode",
    "dynaconf",
    "google-cloud-texttospeech",
    "loguru",
    "openai",
    "pydub",
    "spacy",
    "toml",
    "tqdm",
    "untangle",
]

if sys.version_info < (3, 9):
    requirements.append("importlib-resources")

setup(
    name="podcast2podcast",
    version="0.1.0",
    packages=find_packages(include=["podcast2podcast", "podcast2podcast.*"]),
    install_requires=requirements,
    package_data={"podcast2podcast.data": ["*"]},
)
