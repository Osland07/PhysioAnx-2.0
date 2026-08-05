@echo off
title Install PhysioAnx
echo ==============================================
echo       Memulai Instalasi PhysioAnx...
echo ==============================================
echo.

echo [1/3] Memeriksa Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak terdeteksi! Pastikan Python sudah terinstall dan ditambahkan ke PATH.
    pause
    exit /b
)
echo Python terdeteksi.
echo.

echo [2/3] Membuat Virtual Environment (venv)...
if not exist venv (
    python -m venv venv
    echo Virtual environment berhasil dibuat.
) else (
    echo Virtual environment sudah ada.
)
echo.

echo [3/3] Menginstal dependencies dari requirements.txt...
call .\venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

echo ==============================================
echo Instalasi Selesai!
echo Anda sekarang bisa menjalankan aplikasi dengan
echo mengklik dua kali file "start_app.bat".
echo ==============================================
pause
