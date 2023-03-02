import tempfile

from pydub import AudioSegment


def tts(transcript: str) -> AudioSegment:
    """Convert a transcript to speech using Google's Text-to-Speech API.

    Args:
        transcript (str): Transcript.

    Returns:
        AudioSegment: Audio of the transcript

    """

    from google.cloud import texttospeech as tts

    client = tts.TextToSpeechClient()
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)
    voice = tts.VoiceSelectionParams(
        language_code="en-US", ssml_gender=tts.SsmlVoiceGender.MALE
    )
    response = client.synthesize_speech(
        input=tts.SynthesisInput(text=transcript),
        voice=voice,
        audio_config=audio_config,
    )
    with tempfile.NamedTemporaryFile() as t:
        t.write(response.audio_content)
        audio = AudioSegment.from_wav(t.name)

    return audio
