@echo off
title PhysioAnx
echo Run App...
echo.

:: Mengaktifkan Virtual Environment
call .\venv\Scripts\activate.bat

:: Menjalankan script Flet dengan Hot Reload
cd src
flet run -d --assets ../assets main.py

:: Pause digunakan agar jika ada error, jendela terminal tidak langsung tertutup
pause
