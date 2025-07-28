#!/usr/bin/env python3

import numpy as np
import plotly.graph_objs as go
import librosa
from scipy.fft import rfft, rfftfreq
from scipy import signal

def generate_waveform(y, sr, time_range=None, downsample_factor=10):
    """
    Genera figura Plotly para waveform, aplicando downsampling para acelerar.

    """
    if time_range is None:
        y_segment = y
        start_time = 0
    else:
        start_sample = int(time_range[0] * sr)
        end_sample = int(time_range[1] * sr)
        y_segment = y[start_sample:end_sample]
        start_time = time_range[0]

    # Downsample para acelerar trazado y reducir cantidad de puntos
    y_down = y_segment[::downsample_factor]
    n_points = len(y_down)

    # Tiempo con np.arange a paso downsample
    time = np.arange(n_points) * downsample_factor / sr + start_time

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time,
        y=y_down,
        fill='tozeroy',
        line=dict(color='rgb(40, 120, 181)')
    ))

    fig.update_layout(
        title='Waveform',
        xaxis_title='Time (s)',
        yaxis_title='Amplitude',
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        template='plotly_white'
    )

    return fig

def generate_spectrogram(y, sr, time_range=None, n_fft=512, hop_length=256):
    """
    Genera figura Plotly para espectrograma usando librosa.stft, hop_length para acelerar.
    """
    if time_range is None:
        y_segment = y
        start_time = 0
    else:
        start_sample = int(time_range[0] * sr)
        end_sample = int(time_range[1] * sr)
        y_segment = y[start_sample:end_sample]
        start_time = time_range[0]

    S = np.abs(librosa.stft(y_segment, n_fft=n_fft, hop_length=hop_length))
    S_db = librosa.amplitude_to_db(S, ref=np.max)

    times = librosa.times_like(S_db, sr=sr, hop_length=hop_length, n_fft=n_fft)
    times += start_time

    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    fig = go.Figure(data=go.Heatmap(
        z=S_db,
        x=times,
        y=freqs,
        colorscale='Viridis',
        zmin=-80,
        zmax=0
    ))

    fig.update_layout(
        title=f'Spectrogram',
        xaxis_title='Time (s)',
        yaxis_title='Frequency (Hz)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        template='plotly_white'
    )

    return fig

def plot_power_spectrum(audio_signal, samplerate, filename, show=False):
    """
    Grafica espectro de potencia usando FFT y Plotly.
    """
    N = len(audio_signal)
    yf = rfft(audio_signal)
    xf = rfftfreq(N, 1 / samplerate)
    power_db = 10 * np.log10((2/N * np.abs(yf))**2 + 1e-12)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xf, y=power_db, line=dict(width=1)))
    fig.update_layout(
        title=f'Power Spectrum: {filename}',
        xaxis_title='Frequency (Hz)',
        yaxis_title='Power (dB)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        template='plotly_white'
    )
    fig.update_xaxes(range=[0, samplerate/2])

    if show:
        fig.show()
    return fig

def plot_psd_welch(audio_signal, samplerate, filename, show=False):
    """
    Grafica PSD usando método de Welch.
    """
    nperseg = 2048
    f, psd = signal.welch(
        audio_signal,
        fs=samplerate,
        window='hann',
        nperseg=nperseg,
        noverlap=nperseg // 2,
        scaling='density'
    )
    psd_db = 10 * np.log10(psd + 1e-12)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=f, y=psd_db, line=dict(width=1)))
    fig.update_layout(
        title=f"PSD (Welch): {filename}",
        xaxis_title='Frequency (Hz)',
        yaxis_title='PSD (dB/Hz)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        template='plotly_white'
    )
    fig.update_xaxes(range=[0, samplerate/2])

    if show:
        fig.show()
    return fig
