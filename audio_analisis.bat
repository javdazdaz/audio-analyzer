@echo off



start "" http://127.0.0.1:8050/
REM Ejecutar la aplicación con python -m para resolver imports
python -m app.main


REM Abrir navegador en la URL de la app

REM Pausar para que veas errores (opcional, quita si quieres que cierre rápido)
pause
