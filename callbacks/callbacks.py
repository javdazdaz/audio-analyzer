#!/usr/bin/env python3

import numpy as np
from dash import callback, Input, Output, State, html
from utils.audio_utils import parse_audio
from visualization.plot import generate_waveform, generate_spectrogram, plot_power_spectrum, plot_psd_welch

@callback(
    Output('audio-data', 'data'),
    Output('output-audio-upload', 'children'),
    Output('audio-player', 'url'),
    Output('audio-player', 'style'),
    Input('upload-audio', 'contents'),
    State('upload-audio', 'filename'),
)
def update_audio_data(contents, filename):
    if not contents:
        return None, "", None, {'display': 'none'}

    y, sr = parse_audio(contents, filename)
    if y is None:
        return None, "Error processing audio file", None, {'display': 'none'}

    return {
        'y': y.tolist(),
        'sr': sr
    }, html.Div([
        html.Hr(),
        html.Div(f"File loaded: {filename}")
    ]), contents, {'width': '100%', 'display': 'block'}

@callback(
    Output('audio-current-time', 'data'),
    Input('audio-player', 'currentTime')
)
def capture_current_time(current_time):
    return current_time if current_time else 0

@callback(
    Output('waveform-graph', 'figure'),
    Output('spectrogram-graph', 'figure'),
    Output('fft-graph', 'figure'),
    Output('spectral-density-graph', 'figure'),
    Input('audio-data', 'data'),
    Input('waveform-graph', 'relayoutData'),
    Input('spectrogram-graph', 'relayoutData'),
    Input('audio-player', 'currentTime'),
)
def update_graphs(audio_data, waveform_relayout, spectrogram_relayout, current_time):
    if not audio_data:
        # Regresar figuras vacías
        return {}, {}, {}, {}

    y = np.array(audio_data['y'])
    sr = audio_data['sr']

    time_range = None
    total_duration = len(y) / sr

    for relayout in (waveform_relayout, spectrogram_relayout):
        if relayout:
            if 'xaxis.range[0]' in relayout and 'xaxis.range[1]' in relayout:
                time_range = [float(relayout['xaxis.range[0]']), float(relayout['xaxis.range[1]'])]
            elif 'xaxis.autorange' in relayout:
                time_range = None

    # Ajustar current_time si está fuera de rango de zoom
    adjusted_time = current_time
    if time_range and current_time:
        zoom_start, zoom_end = time_range
        if not (zoom_start <= current_time <= zoom_end):
            adjusted_time = zoom_start + (current_time / total_duration) * (zoom_end - zoom_start)

    waveform_fig = generate_waveform(y, sr, time_range)
    spectrogram_fig = generate_spectrogram(y, sr, time_range)

    if current_time:
        line_shape = dict(
            type='line',
            x0=current_time,
            x1=current_time,
            y0=0,
            y1=1,
            xref='x',
            yref='paper',
            line=dict(color='red', width=2)
        )
        waveform_fig['layout']['shapes'] = [line_shape]
        spectrogram_fig['layout']['shapes'] = [line_shape]

    if time_range:
        start_idx = int(time_range[0] * sr)
        end_idx = int(time_range[1] * sr)
        y_segment = y[start_idx:end_idx]
    else:
        y_segment = y

    fft_fig = plot_power_spectrum(y_segment, sr, "Audio Segment", show=False)
    psd_fig = plot_psd_welch(y_segment, sr, "Audio Segment", show=False)

    for fig in [fft_fig, psd_fig]:
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=300,
            showlegend=False,
            template='plotly_white'
        )

    return waveform_fig, spectrogram_fig, fft_fig, psd_fig
