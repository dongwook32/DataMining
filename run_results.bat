@echo off
chcp 65001 > nul
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" show_results.py
) else (
    python show_results.py
)
echo.
pause

