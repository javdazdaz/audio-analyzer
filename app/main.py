#!/usr/bin/env python3

from dash import Dash
from components.layout import layout
import callbacks.callbacks  # Importa para registrar callbacks (side effects)
import config


def create_app():
    app = Dash(
        __name__,
        assets_folder='../assets',
        suppress_callback_exceptions=True
    )
    app.title = 'Audio Analyzer'
    app.layout = layout
    return app

app = create_app()  # gunicorn

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
