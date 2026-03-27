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
    goto :cleanup
)

where pip >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: pip not found on PATH.
    echo Ensure Python was installed with pip enabled.
    goto :cleanup
)

if not exist "jupyter.ico" (
    echo ERROR: jupyter.ico not found in %CD%.
    echo Ensure the repository was cloned correctly.
    goto :cleanup
)

if not exist "jupyter_tray.py" (
    echo ERROR: jupyter_tray.py not found in %CD%.
    echo Ensure the repository was cloned correctly.
    goto :cleanup
)

echo    Prerequisites OK.

:: --- Install Jupyter Notebook ---
echo.
echo [2/5] Installing Jupyter Notebook...
pip install notebook==6.5.7 pystray Pillow
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERROR: Failed to install Jupyter Notebook.
    echo Check your internet connection and Python installation.
    goto :cleanup
)
echo    Jupyter Notebook installed.

:: --- Verify Jupyter Works ---
echo.
echo [3/5] Verifying Jupyter installation...
jupyter --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo WARNING: Jupyter installed but not found on PATH.
    echo You may need to add Python Scripts directory to your PATH.
    echo Typically: %%USERPROFILE%%\AppData\Local\Programs\Python\PythonXXX\Scripts
    goto :cleanup
)
echo    Jupyter verified.

:: --- Generate Dynamic Registry File ---
echo.
echo [4/5] Generating registry entries...

set "INSTALL_DIR=%~dp0"
if "!INSTALL_DIR:~-1!"=="\" set "INSTALL_DIR=!INSTALL_DIR:~0,-1!"
set "REG_PATH=!INSTALL_DIR:\=\\!"

(
echo Windows Registry Editor Version 5.00
echo.
echo [HKEY_CLASSES_ROOT\Directory\Background\shell\Open Jupyter]
echo @="Open with Jupyter"
echo "Icon"="!REG_PATH!\\jupyter.ico"
echo.
echo [HKEY_CLASSES_ROOT\Directory\Background\shell\Open Jupyter\command]
echo @="pythonw \"!REG_PATH!\\jupyter_tray.py\" \"%%V\""
echo.
echo [HKEY_CLASSES_ROOT\Directory\shell\Open Jupyter]
echo @="Open with Jupyter"
echo "Icon"="!REG_PATH!\\jupyter.ico"
echo.
echo [HKEY_CLASSES_ROOT\Directory\shell\Open Jupyter\command]
echo @="pythonw \"!REG_PATH!\\jupyter_tray.py\" \"%%1\""
) > "%temp%\jupyter-context-menu.reg"

:: --- Import Registry ---
echo.
echo [5/5] Installing context menu...
reg import "%temp%\jupyter-context-menu.reg"
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERROR: Failed to import registry entries.
    echo Make sure you are running as Administrator.
    goto :cleanup
)

echo.
echo ============================================
echo   SUCCESS! Context menu installed.
echo ============================================
echo.
echo Right-click any folder or desktop background
echo and select "Open with Jupyter" to launch
echo Jupyter Notebook with a system tray icon.
echo.

:cleanup
    if exist "%temp%\jupyter-context-menu.reg" del "%temp%\jupyter-context-menu.reg"
    if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs"
    endlocal
    pause
