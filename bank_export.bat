@echo off
set /p MAAND="Geef de maand in (MM/YYYY, of Enter voor huidige maand): "

if "%MAAND%"=="" (
    python bank_export.py
) else (
    python bank_export.py --maand %MAAND%
)

pause