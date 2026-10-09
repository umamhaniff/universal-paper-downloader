@echo off
title Pasang Shortcut Universal Paper Downloader
cd /d "%~dp0"

echo ======================================================================
echo   MEMASANG SHORTCUT START MENU - UNIVERSAL PAPER DOWNLOADER
echo ======================================================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { $ws = New-Object -ComObject WScript.Shell; $lnkPath = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Universal Paper Downloader.lnk'; $s = $ws.CreateShortcut($lnkPath); $curr = (Get-Location).Path; $s.TargetPath = Join-Path $curr 'Universal_Downloader.bat'; $s.WorkingDirectory = $curr; $s.IconLocation = (Join-Path $curr 'assets\app_icon.ico') + ',0'; $s.Description = 'Universal Paper Downloader (Hans x Gravi)'; $s.Save(); Write-Host '[✓] Berhasil! Shortcut berlogo resmi telah terpasang di Windows Start Menu.' -ForegroundColor Green; Write-Host '    Kamu sekarang bisa mencarinya di Windows Search / Start Menu!' -ForegroundColor Cyan }"

echo.
pause
