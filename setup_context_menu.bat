@echo off
echo Installing Jupyter context menu...
reg import open-with-jupyter.reg
if %ERRORLEVEL%==0 (
    echo Context menu installed successfully.
) else (
    echo Failed to install context menu.
)
pause