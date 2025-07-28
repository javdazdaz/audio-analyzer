from dash import html, dcc
import dash_player

layout = html.Div([
    html.H1(
        "Audio Analysis Dashboard",
        style={'textAlign': 'center', 'margin': '20px 0'}
    ),

    dcc.Upload(
        id='upload-audio',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Audio File')
        ]),
        style={
            'width': '80%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '20px auto',
            'display': 'block',
            'cursor': 'pointer',
        },
        multiple=False
    ),

    html.Div(id='output-audio-upload'),

    dash_player.DashPlayer(
        id='audio-player',
        controls=True,
        width='100%',
        height='60px',
        style={'display': 'none', 'margin': '20px 0'}
    ),

    # Stores para guardar tiempo actual, datos de audio, y zooms ejes X e Y
    dcc.Store(id='audio-current-time', data=0),
    dcc.Store(id='audio-data'),

    # Stores para zooms en waveform
    dcc.Store(id='waveform-zoom-x', data=None),
    dcc.Store(id='waveform-zoom-y', data=None),

    # Stores para zooms en spectrogram
    dcc.Store(id='spectrogram-zoom-x', data=None),
    dcc.Store(id='spectrogram-zoom-y', data=None),

    # Stores para zooms en fft
    dcc.Store(id='fft-zoom-x', data=None),
    dcc.Store(id='fft-zoom-y', data=None),

    # Stores para zooms en psd
    dcc.Store(id='psd-zoom-x', data=None),
    dcc.Store(id='psd-zoom-y', data=None),

    # Añade Storage para guardar figuras cacheadas (sin zoom)
    dcc.Store(id='waveform-fig-cache'),
    dcc.Store(id='spectrogram-fig-cache'),

    dcc.Store(id='common-zoom-x', data=None),  # Zoom sincronizado en X para waveform y spectrogram
# Contenedores de gráficos divididos para mejor layout
    html.Div([
        html.Div(
            dcc.Graph(id='waveform-graph'),
            style={'width': '49%', 'display': 'inline-block'}
        ),
        html.Div(
            dcc.Graph(id='spectrogram-graph'),
            style={'width': '49%', 'display': 'inline-block', 'float': 'right'}
        ),
    ], style={'marginBottom': '20px'}),

    html.Div([
        html.Div(
            dcc.Graph(id='fft-graph'),
            style={'width': '49%', 'display': 'inline-block'}
        ),
        html.Div(
            dcc.Graph(id='spectral-density-graph'),
            style={'width': '49%', 'display': 'inline-block', 'float': 'right'}
        ),
    ]),

], style={'padding': '20px'})
