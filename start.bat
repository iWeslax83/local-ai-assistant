@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [*] Yerel AI Asistan baslatiliyor...
echo.

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Ollama bulunamadi. https://ollama.com adresinden indirin.
    exit /b 1
)

curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Ollama baslatiliyor...
    start /b ollama serve
    timeout /t 3 /nobreak >nul
)

ollama list 2>nul | findstr "llama3.1:8b" >nul
if %errorlevel% neq 0 (
    echo [*] Llama 3.1 8B modeli indiriliyor...
    ollama pull llama3.1:8b
)

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo [*] Core API baslatiliyor...
start /b cmd /c "cd core && uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 2 /nobreak >nul

echo [*] Scheduler baslatiliyor...
start /b cmd /c "python scheduler\main.py"

echo [*] WhatsApp Bot baslatiliyor...
start /b cmd /c "cd bot && npm start"

echo.
echo [OK] Tum servisler baslatildi!
echo    - Core API:   port 8000
echo    - Scheduler:  calisiyor
echo    - WhatsApp:   port 3000
echo.
echo [*] WhatsApp QR kodunu tarayin...
echo    Durdurmak icin bu pencereyi kapatin.

pause
