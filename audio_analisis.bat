@echo off


REM Ejecutar la aplicación con python -m para resolver imports
python -m app.main


REM Esperar unos segundos para levantar el servidor antes de abrir navegador
timeout /t 5 /nobreak >nul

REM Abrir navegador en la URL de la app
start "" http://127.0.0.1:8050/

REM Pausar para que veas errores (opcional, quita si quieres que cierre rápido)
pause
