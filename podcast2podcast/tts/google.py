def text2speech_pipeline(transcript: str, fp_out="./podcast.mp3"):
    """Convert a transcript to speech.

    Args:
        transcript (str): Transcript.
        fp_out (str, optional): Path to output audio file. Defaults to "./podcast.mp3".

    Returns:
        str: Path to output audio file.

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
    with open(fp_out, "wb") as f:
        f.write(response.audio_content)

    return fp_out
