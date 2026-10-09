@echo off
title TNP - Trust No Plaintext
color 06

echo ==============================================================
echo    TNP: TRUST NO PLAINTEXT
echo    Enterprise Cryptographic Operations Vault
echo    Sovereign Zero-Trust Cryptographic Suite
echo ==============================================================
echo.

echo [1/3] Memeriksa instalasi Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan! Pastikan Python telah terpasang di PATH.
    pause
    exit /b
)

echo [2/3] Memeriksa dan memasang pustaka (Flask, NumPy, Pillow)...
python -m pip install -r requirements.txt >nul 2>&1

echo [3/3] Menjalankan server TNP di http://127.0.0.1:5000...
echo.
echo ==============================================================
echo    Aplikasi aktif! Membuka browser otomatis dalam 2 detik...
echo    Tekan CTRL + C di terminal ini jika ingin menghentikan.
echo ==============================================================
echo.

start "" http://127.0.0.1:5000
python app.py

pause
