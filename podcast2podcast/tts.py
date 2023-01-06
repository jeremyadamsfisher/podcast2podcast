def text2speech_pipeline(transcript: str, fp_out="./podcast.mp3"):
    """Convert a transcript to speech.

    Args:
        transcript (str): Transcript.
        fp_out (str, optional): Path to output audio file. Defaults to "./podcast.mp3".

    Returns:
        str: Path to output audio file.

    """
    from google.cloud import texttospeech as tts
    from pydub import AudioSegment
    from tqdm import tqdm

    client = tts.TextToSpeechClient()
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)
    voices = {
        "Alice": tts.VoiceSelectionParams(
            language_code="en-US", ssml_gender=tts.SsmlVoiceGender.FEMALE
        ),
        "James": tts.VoiceSelectionParams(
            language_code="en-US", ssml_gender=tts.SsmlVoiceGender.MALE
        ),
    }

    iter_ = enumerate(transcript.transcript)
    fps = []
    for i, segment in tqdm(list(iter_), unit="transcript"):
        fp_out = f"podcast_{i:03}.mp3"
        response = client.synthesize_speech(
            input=tts.SynthesisInput(text=segment.text),
            voice=voices[segment.speaker],
            audio_config=audio_config,
        )
        with open(fp_out, "wb") as f:
            f.write(response.audio_content)
        fps.append(fp_out)

    sum(AudioSegment.from_mp3(fp) for fp in fps).export(fp_out, format="mp3")

    return fp_out
