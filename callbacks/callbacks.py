import numpy as np
from dash import callback, Input, Output, State, html
from utils.audio_utils import parse_audio
from visualization.plot import generate_waveform, generate_spectrogram, plot_power_spectrum, plot_psd_welch

def extract_zoom_ranges(relayout_data):
    """
    Extrae los rangos de zoom en X e Y de relayoutData si existen.
    Devuelve dict con 'x' y 'y' keys o None.
    """
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
    """
    Aplica rangos de zoom a la figura Plotly (sin sobrescribir si son None).
    """
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

    # Guardamos audio en lista para serialización JSON
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

    Output('waveform-zoom-x', 'data'),
    Output('waveform-zoom-y', 'data'),
    Output('spectrogram-zoom-x', 'data'),
    Output('spectrogram-zoom-y', 'data'),
    Output('fft-zoom-x', 'data'),
    Output('fft-zoom-y', 'data'),
    Output('psd-zoom-x', 'data'),
    Output('psd-zoom-y', 'data'),

    Input('audio-data', 'data'),

    Input('waveform-graph', 'relayoutData'),
    Input('spectrogram-graph', 'relayoutData'),

    Input('audio-player', 'currentTime'),

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
    current_time,
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
        # Reset zoom states si no hay audio
        empty_fig = {}
        return (empty_fig, empty_fig, empty_fig, empty_fig) + (None,)*8

    y = np.array(audio_data['y'])
    sr = audio_data['sr']
    total_duration = len(y)/sr

    # --- Procesar rango de tiempo seleccionado (zoom en X) de waveform o spectrogram ---
    # El zoom puede venir de uno o ambos gráficos, priorizamos la entrada más reciente (waveform > spectrogram)
    time_range = None
    if waveform_relayout and isinstance(waveform_relayout, dict):
        x_range, y_range = extract_zoom_ranges(waveform_relayout)
        if x_range is not None:
            time_range = x_range
            waveform_zoom_x, waveform_zoom_y = x_range, y_range
    elif spectrogram_relayout and isinstance(spectrogram_relayout, dict):
        x_range, y_range = extract_zoom_ranges(spectrogram_relayout)
        if x_range is not None:
            time_range = x_range
            spectrogram_zoom_x, spectrogram_zoom_y = x_range, y_range

    # Si 'autorange' activado (reset zoom)
    if waveform_relayout and 'xaxis.autorange' in waveform_relayout:
        waveform_zoom_x, waveform_zoom_y = None, None
        time_range = None
    if spectrogram_relayout and 'xaxis.autorange' in spectrogram_relayout:
        spectrogram_zoom_x, spectrogram_zoom_y = None, None
        time_range = None

    # --- Ajustar posición actual del audio que marca la línea roja ---
    adjusted_time = current_time
    if time_range and current_time is not None:
        zoom_start, zoom_end = time_range
        if current_time < zoom_start or current_time > zoom_end:
            # Ajuste proporcional simple
            adjusted_time = zoom_start + (current_time / total_duration) * (zoom_end - zoom_start)

    # --- Selección de segmento para FFT y PSD ---
    if time_range:
        start_sample = int(max(time_range[0]*sr, 0))
        end_sample = int(min(time_range[1]*sr, len(y)))
        segment = y[start_sample:end_sample]
    else:
        segment = y

    # --- Generar figuras ---
    waveform_fig = generate_waveform(y, sr, time_range)
    spectrogram_fig = generate_spectrogram(y, sr, time_range)

    fft_fig = plot_power_spectrum(segment, sr, "Audio Segment", show=False)
    psd_fig = plot_psd_welch(segment, sr, "Audio Segment", show=False)

    # Añadir línea roja tiempo actual ajustado (si tiene sentido)
    for fig in [waveform_fig, spectrogram_fig]:
        shapes = fig.layout.shapes or []
        # Usar adjusted_time para línea marcada
        if adjusted_time is not None:
            line_shape = dict(
                type='line',
                x0=adjusted_time, x1=adjusted_time,
                y0=0, y1=1,
                xref='x',
                yref='paper',
                line=dict(color='red', width=2)
            )
            shapes = [line_shape]
        fig.update_layout(shapes=shapes)

    # --- Reaplicar zoom Y y X guardados a todas las figuras ---
    waveform_fig = apply_zoom_to_fig(waveform_fig, waveform_zoom_x, waveform_zoom_y)
    spectrogram_fig = apply_zoom_to_fig(spectrogram_fig, spectrogram_zoom_x, spectrogram_zoom_y)
    fft_fig = apply_zoom_to_fig(fft_fig, fft_zoom_x, fft_zoom_y)
    psd_fig = apply_zoom_to_fig(psd_fig, psd_zoom_x, psd_zoom_y)

    # Uniformizar estilos generales (alturas, márgenes, template)
    for fig in [fft_fig, psd_fig]:
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=300,
            showlegend=False,
            template='plotly_white'
        )

    # --- Salida ---
    return (
        waveform_fig,
        spectrogram_fig,
        fft_fig,
        psd_fig,
        waveform_zoom_x,
        waveform_zoom_y,
        spectrogram_zoom_x,
        spectrogram_zoom_y,
        fft_zoom_x,
        fft_zoom_y,
        psd_zoom_x,
        psd_zoom_y,
    )
