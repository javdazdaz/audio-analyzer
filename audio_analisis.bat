@echo off
REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ir a la carpeta app (opcional, para claridad)
cd app

REM Ejecutar la aplicación con python -m para resolver imports
python -m main

REM Pausar para que veas errores (opcional, quita si quieres que cierre rápido)
pause
