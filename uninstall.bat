@echo off
setlocal enabledelayedexpansion

:: ============================================
:: Jupyter Notebook - Context Menu Uninstaller
:: ============================================

:: --- Admin Check ---
net session >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo Requesting administrative privileges...
    goto :UACPrompt
)
goto :gotAdmin

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs"
    CD /D "%~dp0"

echo.
echo ============================================
echo   Jupyter Context Menu - Uninstall
echo ============================================
echo.

:: --- Stop running Jupyter tray instances ---
echo [1/3] Stopping running Jupyter instances...
powershell -Command "Get-CimInstance Win32_Process -Filter \"CommandLine LIKE '%%jupyter_tray.py%%'\" -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" >nul 2>&1
echo    Done.

:: --- Remove Registry Entries & Logs ---
echo.
echo [2/3] Removing context menu entries and logs...
reg delete "HKEY_CLASSES_ROOT\Directory\Background\shell\Open Jupyter" /f >nul 2>&1
reg delete "HKEY_CLASSES_ROOT\Directory\shell\Open Jupyter" /f >nul 2>&1
if exist "%LOCALAPPDATA%\JupyterContext" rmdir /s /q "%LOCALAPPDATA%\JupyterContext" >nul 2>&1
echo    Context menu entries and logs removed.

:: --- Optionally Uninstall Jupyter ---
echo.
echo [3/3] Jupyter Notebook package...
echo.
set /P "UNINSTALL_PIP=Also uninstall Jupyter Notebook and dependencies? (Y/N): "
if /I "!UNINSTALL_PIP!"=="Y" (
    python -m pip uninstall notebook pystray Pillow -y >nul 2>&1
    echo    Packages uninstalled.
) else (
    echo    Packages kept.
)

echo.
echo ============================================
echo   Uninstall complete.
echo ============================================
echo.
echo You may delete this folder if no longer needed.
echo.

:cleanup
    if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs"
    endlocal
    pause
