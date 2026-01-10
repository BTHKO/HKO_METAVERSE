@echo off
setlocal enabledelayedexpansion

echo ================================
echo   HKO Grunt v10 - EXE Builder
echo ================================
echo.

:: Detect the folder where this BAT is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo Working directory:
echo %SCRIPT_DIR%
echo.

:: Clean old build folders
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec 2>NUL

echo Cleaned previous build...
echo.

:: Detect python executable
for %%P in (python.exe python3.exe py.exe) do (
    where %%P >NUL 2>&1
    if !errorlevel! == 0 (
        set PYTHON_CMD=%%P
        goto found_python
    )
)

echo ERROR: No Python installation found.
pause
exit /b

:found_python
echo Using Python: %PYTHON_CMD%
echo.

:: Detect grunt python file
set GRUNT_FILE=
for %%F in (*.py) do (
    if /i "%%~nF"=="HKO_Grunt_v10" (
        set GRUNT_FILE=%%F
    )
)

if "%GRUNT_FILE%"=="" (
    echo ERROR: Could not find HKO_Grunt_v10.py in this folder.
    pause
    exit /b
)

echo Building EXE from: %GRUNT_FILE%
echo.

:: RUN PyInstaller
%PYTHON_CMD% -m PyInstaller --noconsole --onefile "%GRUNT_FILE%"
echo.

if not exist dist (
    echo ERROR: Build failed. No dist folder created.
    pause
    exit /b
)

echo Build COMPLETE!
echo Your EXE is here:
echo   %SCRIPT_DIR%dist\HKO_Grunt_v10.exe
echo.

pause
exit /b
