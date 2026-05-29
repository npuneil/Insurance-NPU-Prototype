@echo off
echo ╔══════════════════════════════════════════════════════════════╗
echo ║   Zava Insurance - On-Device AI Demo  (Snapdragon Edition) ║
echo ║   Optimized for Snapdragon X NPU (QNN runtime)             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM ── Activate venv ──
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found. Run Setup.bat first.
    pause
    exit /b 1
)

REM ── Tell the app which silicon it's running on ──
set ZAVA_PLATFORM=snapdragon

REM ── Launch browser after short delay ──
start "" "http://localhost:5000"

REM ── Start Flask app ──
echo [Starting] Flask app on http://localhost:5000
echo [INFO] Platform: Snapdragon X (QNN NPU)
echo [INFO] Foundry Local model loading may take a moment on first run.
echo [INFO] The browser page will work once the app finishes loading.
echo [INFO] Close this window to stop the app.
echo.
python app.py
