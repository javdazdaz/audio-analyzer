#!/usr/bin/env python3

from dash import html, dcc
import dash_player

layout = html.Div([
    html.H1("Audio Analysis Dashboard", style={'textAlign': 'center', 'margin': '20px 0'}),

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

    dcc.Store(id='audio-current-time', data=0),

    html.Div([
        html.Div(dcc.Graph(id='waveform-graph'), style={'width': '49%', 'display': 'inline-block'}),
        html.Div(dcc.Graph(id='spectrogram-graph'), style={'width': '49%', 'display': 'inline-block', 'float': 'right'}),
    ]),

    html.Div([
        html.Div(dcc.Graph(id='fft-graph'), style={'width': '49%', 'display': 'inline-block'}),
        html.Div(dcc.Graph(id='spectral-density-graph'), style={'width': '49%', 'display': 'inline-block', 'float': 'right'}),
    ]),

    dcc.Store(id='audio-data'),
    dcc.Store(id='current-time-range'),
    dcc.Store(id='fft-cache'),
    dcc.Store(id='psd-cache'),
], style={'padding': '20px'})
