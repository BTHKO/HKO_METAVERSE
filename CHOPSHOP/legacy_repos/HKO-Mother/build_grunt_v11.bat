@echo off
title HKO Grunt v11 - Builder

echo Cleaning previous build...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul

echo Building EXE...
python -m PyInstaller --onefile --noconsole HKO_Grunt_v11.py

echo Build Complete.
pause
