@echo off
setlocal EnableDelayedExpansion
title Universal Paper Downloader - Hans x Gravi

:: Pastikan berjalan di folder skrip berada
cd /d "%~dp0"

:: Cek apakah Python terpasang di sistem
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ======================================================================
    echo  [!] PERINGATAN: Python tidak ditemukan di PATH sistem!
    echo  Silakan instal Python 3.8+ dari https://www.python.org/downloads/
    echo ======================================================================
    echo.
    pause
    exit /b 1
)

:MENU
cls
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { Write-Host '======================================================================' -ForegroundColor Cyan; Write-Host '             UNIVERSAL PAPER DOWNLOADER (Hans x Gravi)                ' -ForegroundColor Yellow; Write-Host '======================================================================' -ForegroundColor Cyan; Write-Host '  Engine: 5-Tier Waterfall | Cross-Publisher | Strict 8GB RAM Optimized' -ForegroundColor DarkGray; Write-Host '======================================================================' -ForegroundColor Cyan }"

echo.
echo   [1] Unduh Paper Satuan (DOI / URL Nature, ScienceDirect, IEEE, dll)
echo   [2] Unduh 1 Edisi Jurnal Penuh IEEE (Auto-Merge Master PDF)
echo   [3] Unduh Batch (Banyak DOI sekaligus dari file teks)
echo   [4] Buka Folder Penyimpanan PDF (File Explorer)
echo   [5] Keluar
echo.
echo ======================================================================

set /p choice="Pilih menu (1-5) [Default: 1] > "
if "%choice%"=="" set choice=1

if "%choice%"=="1" goto DOWNLOAD_SINGLE
if "%choice%"=="2" goto DOWNLOAD_IEEE_ISSUE
if "%choice%"=="3" goto DOWNLOAD_BATCH
if "%choice%"=="4" goto OPEN_FOLDER
if "%choice%"=="5" goto EXIT_APP
if /i "%choice%"=="q" goto EXIT_APP

echo.
echo [!] Pilihan tidak valid. Silakan pilih nomor 1 sampai 5.
timeout /t 2 >nul
goto MENU

:DOWNLOAD_SINGLE
cls
python universal_downloader.py
goto RETURN_CHECK

:DOWNLOAD_IEEE_ISSUE
cls
echo ======================================================================
echo          UNDUH 1 EDISI PENUH JURNAL IEEE (MERGE PDF MASTER)
echo ======================================================================
echo Masukkan link issue IEEE (Contoh: tocresult.jsp?isnumber=...^&punumber=...)
echo Atau tekan Enter untuk input interaktif via python:
echo.
set /p issue_url="Link Issue IEEE > "
if "%issue_url%"=="" (
    python universal_downloader.py
) else (
    python universal_downloader.py "%issue_url%"
)
goto RETURN_CHECK

:DOWNLOAD_BATCH
cls
echo ======================================================================
echo              UNDUH BATCH DARI FILE DAFTAR DOI (.TXT)
echo ======================================================================
echo Masukkan path file teks (Contoh: daftar_doi.txt)
echo Atau tekan Enter untuk memakai 'daftar_doi.txt':
echo.
set /p batch_file="Path File Teks [Default: daftar_doi.txt] > "
if "%batch_file%"=="" set batch_file=daftar_doi.txt

if not exist "%batch_file%" (
    echo.
    echo [!] File '%batch_file%' tidak ditemukan di folder ini!
    echo Buat file teks terlebih dahulu dengan 1 DOI/URL per baris.
    echo.
    pause
    goto MENU
)

python universal_downloader.py --file "%batch_file%"
goto RETURN_CHECK

:OPEN_FOLDER
echo.
echo [*] Membuka folder output PDF di File Explorer...
if not exist "pdf_output" mkdir "pdf_output"
start "" "pdf_output"
timeout /t 1 >nul
goto MENU

:RETURN_CHECK
echo.
echo ======================================================================
echo   [1] / [Enter] : Kembali ke Menu Utama
echo   [2] / [q]     : Tutup Jendela Program
echo ======================================================================
set /p post_choice="Pilihan kamu (1/2) [Default: 1] > "
if "%post_choice%"=="" goto MENU
if "%post_choice%"=="1" goto MENU
if "%post_choice%"=="2" goto EXIT_APP
if /i "%post_choice%"=="q" goto EXIT_APP
goto MENU

:EXIT_APP
echo.
echo Terima kasih telah menggunakan Universal Paper Downloader!
echo Sampai jumpa, Hans.
timeout /t 1 >nul
exit /b 0
