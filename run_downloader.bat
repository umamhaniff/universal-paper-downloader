@echo off
:: ========================================================
:: Universal Paper Downloader Launcher
:: Built by Hans x Gravi
:: ========================================================
title Universal Paper Downloader - Hans x Gravi
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { Clear-Host; Write-Host '======================================================================' -ForegroundColor Cyan; Write-Host '             UNIVERSAL PAPER DOWNLOADER (Hans x Gravi)                ' -ForegroundColor Yellow; Write-Host '======================================================================' -ForegroundColor Cyan; Write-Host ''; python universal_downloader.py; Write-Host ''; Write-Host 'Tekan Enter / sembarang tombol untuk menutup jendela...' -ForegroundColor DarkGray; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown'); Exit }"
