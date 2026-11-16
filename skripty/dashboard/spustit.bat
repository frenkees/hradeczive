@echo off
rem Spustí dashboard (http://127.0.0.1:8765/) a ikonu v oznamovací oblasti bez okna konzole.
cd /d "%~dp0..\..\izomapa"
start "" /b ".venv\Scripts\pythonw.exe" "..\skripty\dashboard\tray.py"
