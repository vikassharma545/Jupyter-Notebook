@echo off
setlocal enabledelayedexpansion

:: ============================================
:: Jupyter Notebook - Context Menu Installer
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

:: --- Preflight Checks ---
echo.
echo ============================================
echo   Jupyter Context Menu - Setup
echo ============================================
echo.

echo [1/5] Checking prerequisites...

where python >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Python not found on PATH.
    echo Please install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    goto :fail
)

where pip >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: pip not found on PATH.
    echo Ensure Python was installed with pip enabled.
    goto :fail
)

:: Get full path to pythonw.exe (Explorer may not have user PATH)
set "PYTHONW_PATH="
for /f "tokens=*" %%i in ('where pythonw 2^>nul') do (
    if not defined PYTHONW_PATH set "PYTHONW_PATH=%%i"
)
if not defined PYTHONW_PATH (
    echo ERROR: pythonw.exe not found on PATH.
    echo Ensure Python was installed correctly.
    goto :fail
)

if not exist "jupyter.ico" (
    echo ERROR: jupyter.ico not found in %CD%.
    echo Ensure the repository was cloned correctly.
    goto :fail
)

if not exist "jupyter_tray.py" (
    echo ERROR: jupyter_tray.py not found in %CD%.
    echo Ensure the repository was cloned correctly.
    goto :fail
)

echo    OK
echo    pythonw: !PYTHONW_PATH!

:: --- Install Dependencies ---
echo.
echo [2/5] Installing dependencies...
pip install notebook==6.5.7 pystray Pillow
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERROR: pip install failed.
    echo Check your internet connection and Python installation.
    goto :fail
)
echo    Dependencies installed.

:: --- Verify Jupyter Works ---
echo.
echo [3/5] Verifying Jupyter installation...
jupyter --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERROR: Jupyter not found on PATH after install.
    echo You may need to add Python Scripts directory to your PATH.
    goto :fail
)
echo    Jupyter verified.

:: --- Remove old entries first (clean re-install) ---
echo.
echo [4/5] Generating registry entries...
reg delete "HKEY_CLASSES_ROOT\Directory\Background\shell\Open Jupyter" /f >nul 2>&1
reg delete "HKEY_CLASSES_ROOT\Directory\shell\Open Jupyter" /f >nul 2>&1

:: --- Generate Dynamic Registry File ---
set "INSTALL_DIR=%~dp0"
if "!INSTALL_DIR:~-1!"=="\" set "INSTALL_DIR=!INSTALL_DIR:~0,-1!"
set "REG_PATH=!INSTALL_DIR:\=\\!"
set "PYTHONW_REG=!PYTHONW_PATH:\=\\!"

(
echo Windows Registry Editor Version 5.00
echo.
echo [HKEY_CLASSES_ROOT\Directory\Background\shell\Open Jupyter]
echo @="Open with Jupyter"
echo "Icon"="!REG_PATH!\\jupyter.ico"
echo.
echo [HKEY_CLASSES_ROOT\Directory\Background\shell\Open Jupyter\command]
echo @="\"!PYTHONW_REG!\" \"!REG_PATH!\\jupyter_tray.py\" \"%%V\""
echo.
echo [HKEY_CLASSES_ROOT\Directory\shell\Open Jupyter]
echo @="Open with Jupyter"
echo "Icon"="!REG_PATH!\\jupyter.ico"
echo.
echo [HKEY_CLASSES_ROOT\Directory\shell\Open Jupyter\command]
echo @="\"!PYTHONW_REG!\" \"!REG_PATH!\\jupyter_tray.py\" \"%%1\""
) > "%temp%\jupyter-context-menu.reg"

:: --- Import Registry ---
echo.
echo [5/5] Installing context menu...
reg import "%temp%\jupyter-context-menu.reg"
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERROR: Failed to import registry entries.
    echo Make sure you are running as Administrator.
    goto :fail
)

echo.
echo ============================================
echo   SUCCESS! Context menu installed.
echo ============================================
echo.
echo   - Right-click any folder or desktop and
echo     select "Open with Jupyter"
echo   - Each folder opens its own Jupyter server
echo   - Look for the Jupyter icon in system tray
echo     (bottom-right near clock)
echo   - Right-click tray icon to stop the server
echo.
goto :cleanup

:fail
echo.
echo ============================================
echo   INSTALLATION FAILED
echo ============================================
echo   See errors above for details.
echo.

:cleanup
    if exist "%temp%\jupyter-context-menu.reg" del "%temp%\jupyter-context-menu.reg"
    if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs"
    endlocal
    pause
