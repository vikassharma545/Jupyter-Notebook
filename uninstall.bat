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

:: --- Remove Registry Entries ---
echo [1/2] Removing context menu entries...

reg delete "HKEY_CLASSES_ROOT\Directory\Background\shell\Open Jupyter" /f >nul 2>&1
reg delete "HKEY_CLASSES_ROOT\Directory\shell\Open Jupyter" /f >nul 2>&1

echo    Context menu entries removed.

:: --- Optionally Uninstall Jupyter ---
echo.
echo [2/2] Jupyter Notebook package...
echo.
set /P "UNINSTALL_PIP=Do you also want to uninstall Jupyter Notebook? (Y/N): "
if /I "!UNINSTALL_PIP!"=="Y" (
    pip uninstall notebook -y
    echo    Jupyter Notebook uninstalled.
) else (
    echo    Jupyter Notebook was kept installed.
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
