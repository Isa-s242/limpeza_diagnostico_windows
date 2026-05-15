@echo off
:: ============================================================
::  BUILD — Limpeza e Diagnóstico Windows
::  Converte o script Python em EXE standalone via PyInstaller
:: ============================================================

echo.
echo  [BUILD] Instalando dependencias...
pip install pyinstaller --quiet

echo  [BUILD] Compilando executavel...
pyinstaller ^
    --onefile ^
    --console ^
    --uac-admin ^
    --name "LimpezaDiagnosticoWindows" ^
    --icon NONE ^
    limpeza_diagnostico_windows.py

echo.
echo  [BUILD] Concluido!
echo  O executavel esta em: dist\LimpezaDiagnosticoWindows.exe
echo.
pause
