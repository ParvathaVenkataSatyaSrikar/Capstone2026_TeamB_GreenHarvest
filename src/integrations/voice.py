"""Speech-to-text for farmer voice questions — optional dependency."""
from __future__ import annotations

import io
from typing import Optional

# BCP-47 style codes for Google Web Speech API (via SpeechRecognition)
LANG_TO_SR = {
    "english": "en-IN",
    "hindi": "hi-IN",
    "telugu": "te-IN",
    "tamil": "ta-IN",
    "marathi": "mr-IN",
    "punjabi": "pa-IN",
}


def transcribe_audio_bytes(
    audio_bytes: bytes,
    language: str = "english",
) -> tuple[Optional[str], Optional[str]]:
    """
    Transcribe WAV bytes from st.audio_input.
    Returns (text, error_message).
    """
    if not audio_bytes:
        return None, "No audio recorded."

    try:
        import speech_recognition as sr
    except ImportError:
        return None, (
            "Voice needs the SpeechRecognition package. "
            "Run: pip install SpeechRecognition — or type your question."
        )

    recognizer = sr.Recognizer()
    lang_code = LANG_TO_SR.get((language or "english").lower(), "en-IN")

    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language=lang_code)
        text = (text or "").strip()
        if not text:
            return None, "Could not understand audio. Try again or type your question."
        return text, None
    except sr.UnknownValueError:
        return None, "Could not understand audio. Speak clearly or type your question."
    except sr.RequestError as e:
        return None, f"Speech service unavailable ({e}). Type your question instead."
    except Exception as e:
        return None, f"Could not process audio ({e}). Use text input."
