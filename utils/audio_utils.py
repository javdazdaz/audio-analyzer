#!/usr/bin/env python3

import base64
import io
import librosa
import logging

def parse_audio(contents: str, filename: str):
    """
    Decodifica contenido base64 y carga audio usando librosa.

    Args:
        contents: String base64 del audio.
        filename: Nombre del archivo (para logs si gusta).

    Returns:
        tuple: (audio_samples numpy array, sample_rate)
    """
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        y, sr = librosa.load(io.BytesIO(decoded), sr=None)
        return y, sr
    except Exception as e:
        logging.error(f"Error processing audio file {filename}: {e}")
        return None, None
