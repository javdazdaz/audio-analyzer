import concurrent.futures

import numpy as np
import plotly.graph_objs as go
from dash import callback, callback_context, html, Input, Output, State

from app.parallel import process_pool
from config import n_segments
from utils.audio_utils import parse_audio
from visualization.plot import (
    generate_spectrogram,
    generate_waveform,
    plot_power_spectrum,
    plot_psd_welch,
)

def fig_from_cache(fig_cache):
    if fig_cache is None:
        return go.Figure()
    return go.Figure(fig_cache)


def extract_zoom_ranges(relayout_data):
    if not relayout_data:
        return None, None

    x0 = relayout_data.get('xaxis.range[0]')
    x1 = relayout_data.get('xaxis.range[1]')
    y0 = relayout_data.get('yaxis.range[0]')
    y1 = relayout_data.get('yaxis.range[1]')

    x_range = [float(x0), float(x1)] if x0 is not None and x1 is not None else None
    y_range = [float(y0), float(y1)] if y0 is not None and y1 is not None else None

    return x_range, y_range


def apply_zoom_to_fig(fig, x_range=None, y_range=None):
    if x_range:
        fig.update_xaxes(range=x_range)
    if y_range:
        fig.update_yaxes(range=y_range)
    return fig


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
    Output('waveform-fig-cache', 'data'),
    Output('spectrogram-fig-cache', 'data'),
    Input('audio-data', 'data')
)
def cache_waveform_spectrogram(audio_data):
    if not audio_data:
        return None, None

    y = np.array(audio_data['y'])
    sr = audio_data['sr']

    waveform_fig = generate_waveform(y, sr, time_range=None)
    spectrogram_fig = generate_spectrogram(y, sr, time_range=None)

    return waveform_fig.to_dict(), spectrogram_fig.to_dict()


# Función para procesar FFT de un segmento (para paralelizar)
def process_segment_fft(segment, sr):
    fft_fig = plot_power_spectrum(segment, sr, "Segment", show=False)
    return fft_fig.to_dict()


@callback(
    Output('common-zoom-x', 'data'),
    Output('waveform-graph', 'figure'),
    Output('spectrogram-graph', 'figure'),
    Output('fft-graph', 'figure'),
    Output('spectral-density-graph', 'figure'),

    Output('waveform-zoom-y', 'data'),
    Output('spectrogram-zoom-y', 'data'),
    Output('fft-zoom-x', 'data'),
    Output('fft-zoom-y', 'data'),
    Output('psd-zoom-x', 'data'),
    Output('psd-zoom-y', 'data'),

    Input('audio-data', 'data'),
    Input('waveform-graph', 'relayoutData'),
    Input('spectrogram-graph', 'relayoutData'),
    Input('waveform-fig-cache', 'data'),
    Input('spectrogram-fig-cache', 'data'),
    Input('audio-player', 'currentTime'),

    State('common-zoom-x', 'data'),
    State('waveform-zoom-x', 'data'),
    State('waveform-zoom-y', 'data'),
    State('spectrogram-zoom-x', 'data'),
    State('spectrogram-zoom-y', 'data'),
    State('fft-zoom-x', 'data'),
    State('fft-zoom-y', 'data'),
    State('psd-zoom-x', 'data'),
    State('psd-zoom-y', 'data'),
)

def update_graphs(
    audio_data,
    waveform_relayout,
    spectrogram_relayout,
    waveform_fig_cache,
    spectrogram_fig_cache,
    current_time,
    common_zoom_x,
    waveform_zoom_x,
    waveform_zoom_y,
    spectrogram_zoom_x,
    spectrogram_zoom_y,
    fft_zoom_x,
    fft_zoom_y,
    psd_zoom_x,
    psd_zoom_y,
):
    if not audio_data:
        empty_fig = go.Figure()
        return (
            common_zoom_x,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            waveform_zoom_y,
            spectrogram_zoom_y,
            fft_zoom_x,
            fft_zoom_y,
            psd_zoom_x,
            psd_zoom_y,
        )

    y = np.array(audio_data['y'])
    sr = audio_data['sr']
    total_duration = len(y) / sr

    ctx = callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    else:
        triggered_id = None

    def get_ranges(relayout):
        if not relayout or not isinstance(relayout, dict):
            return None, None, False, False
        x_range = None
        y_range = None
        autorange_x = 'xaxis.autorange' in relayout
        autorange_y = 'yaxis.autorange' in relayout
        if 'xaxis.range[0]' in relayout and 'xaxis.range[1]' in relayout:
            x_range = [float(relayout['xaxis.range[0]']), float(relayout['xaxis.range[1]'])]
        if 'yaxis.range[0]' in relayout and 'yaxis.range[1]' in relayout:
            y_range = [float(relayout['yaxis.range[0]']), float(relayout['yaxis.range[1]'])]
        return x_range, y_range, autorange_x, autorange_y

    # Actualizamos zooms si se activó alguno
    if triggered_id == 'waveform-graph':
        x_range, y_range, autorange_x, autorange_y = get_ranges(waveform_relayout)
        if autorange_x:
            common_zoom_x = None
        elif x_range is not None:
            common_zoom_x = x_range

        if autorange_y:
            waveform_zoom_y = None
        elif y_range is not None:
            waveform_zoom_y = y_range

    elif triggered_id == 'spectrogram-graph':
        x_range, y_range, autorange_x, autorange_y = get_ranges(spectrogram_relayout)
        if autorange_x:
            common_zoom_x = None
        elif x_range is not None:
            common_zoom_x = x_range

        if autorange_y:
            spectrogram_zoom_y = None
        elif y_range is not None:
            spectrogram_zoom_y = y_range

    # Carga de figuras base
    waveform_fig = fig_from_cache(waveform_fig_cache)
    spectrogram_fig = fig_from_cache(spectrogram_fig_cache)

    triggered = ctx.triggered
    last_trigger = triggered[-1]['prop_id'] if triggered else None

    def get_zoom(relayout):
        if not relayout or not isinstance(relayout, dict):
            return None, None, False, False
        x_range, y_range = extract_zoom_ranges(relayout)
        autorange_x = 'xaxis.autorange' in relayout
        autorange_y = 'yaxis.autorange' in relayout
        return x_range, y_range, autorange_x, autorange_y

    time_range = None

    if (
        last_trigger
        and 'waveform-graph.relayoutData' in last_trigger
        and waveform_relayout
        and isinstance(waveform_relayout, dict)
    ):
        x_range, y_range, autorange_x, autorange_y = get_zoom(waveform_relayout)
        if autorange_x:
            waveform_zoom_x = None
            waveform_zoom_y = None
            time_range = None
        elif x_range is not None:
            waveform_zoom_x = x_range
            waveform_zoom_y = y_range
            time_range = x_range
        spectrogram_zoom_x = None if time_range else spectrogram_zoom_x

    elif (
        last_trigger
        and 'spectrogram-graph.relayoutData' in last_trigger
        and spectrogram_relayout
        and isinstance(spectrogram_relayout, dict)
    ):
        x_range, y_range, autorange_x, autorange_y = get_zoom(spectrogram_relayout)
        if autorange_x:
            spectrogram_zoom_x = None
            spectrogram_zoom_y = None
            time_range = None
        elif x_range is not None:
            spectrogram_zoom_x = x_range
            spectrogram_zoom_y = y_range
            time_range = x_range
        waveform_zoom_x = None if time_range else waveform_zoom_x

    adjusted_time = current_time
    if time_range and current_time is not None:
        zoom_start, zoom_end = time_range
        if current_time < zoom_start or current_time > zoom_end:
            adjusted_time = zoom_start + (current_time / total_duration) * (zoom_end - zoom_start)

    if time_range:
        start_sample = int(max(time_range[0] * sr, 0))
        end_sample = int(min(time_range[1] * sr, len(y)))
        segment = y[start_sample:end_sample]
    else:
        segment = y

    segments = np.array_split(segment, n_segments)

    # Creamos un ThreadPoolExecutor para paralelizar el proceso pesado
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Paralelizar el procesamiento de segmentos FFT
        fft_futures = [executor.submit(process_segment_fft, seg, sr) for seg in segments]

        # Paralelizar la creación de la figura FFT combinada y figura PSD
        future_fft_fig = executor.submit(plot_power_spectrum, segment, sr, "Audio Segment", show=False)
        future_psd_fig = executor.submit(plot_psd_welch, segment, sr, "Audio Segment", show=False)

        # Esperar resultados
        fft_results = [f.result() for f in fft_futures]
        fft_fig = future_fft_fig.result()
        psd_fig = future_psd_fig.result()

    # Aplica zoom a FFT y PSD
    fft_fig = apply_zoom_to_fig(fft_fig, fft_zoom_x, fft_zoom_y)
    psd_fig = apply_zoom_to_fig(psd_fig, psd_zoom_x, psd_zoom_y)
    waveform_fig = fig_from_cache(waveform_fig_cache)
    spectrogram_fig = fig_from_cache(spectrogram_fig_cache)


    for fig in [fft_fig, psd_fig]:
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=300,
            showlegend=False,
            template='plotly_white',
        )

    # Añade línea vertical con adjusted_time
    for fig in [waveform_fig, spectrogram_fig]:
        shapes = []
        if adjusted_time is not None:
            line_shape = dict(
                type='line',
                x0=adjusted_time,
                x1=adjusted_time,
                y0=0,
                y1=1,
                xref='x',
                yref='paper',
                line=dict(color='red', width=2),
            )
            shapes.append(line_shape)
        fig.update_layout(shapes=shapes)

    waveform_fig = apply_zoom_to_fig(waveform_fig, common_zoom_x, waveform_zoom_y)
    spectrogram_fig = apply_zoom_to_fig(spectrogram_fig, common_zoom_x, spectrogram_zoom_y)

    return (
        common_zoom_x,
        waveform_fig,
        spectrogram_fig,
        fft_fig,
        psd_fig,
        waveform_zoom_y,
        spectrogram_zoom_y,
        fft_zoom_x,
        fft_zoom_y,
        psd_zoom_x,
        psd_zoom_y,
    )
