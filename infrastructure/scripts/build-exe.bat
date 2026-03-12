@echo off
setlocal

:: Run from this script's own directory so bb.edn and bb.exe are found
cd /d "%~dp0"

if not exist "bb.exe" (
    echo [X] bb.exe not found in scripts directory.
    echo     Expected: %~dp0bb.exe
    pause
    exit /b 1
)

echo [*] Building spellbook_cli.exe via bb build-exe...
echo.
bb.exe build-exe

echo.
if %ERRORLEVEL% NEQ 0 (
    echo [X] Build failed with error code %ERRORLEVEL%.
) else (
    echo [OK] Build complete: %~dp0spellbook_cli.exe
)
endlocal
pause
