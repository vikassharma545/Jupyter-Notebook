# Open with Jupyter (Windows Context Menu) — No Anaconda Needed

[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?logo=windows&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![No Anaconda](https://img.shields.io/badge/Anaconda-Not%20Required-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Boost your workflow with a single right-click! This project adds an **"Open with Jupyter"** entry to the Windows Explorer context menu so you can launch Jupyter Notebook directly in any folder — no Anaconda required.

The Jupyter server runs **completely hidden** — no terminal window, just a clean **system tray icon** (like Bluetooth) to manage the server.

---

## Requirements

- Windows 10 or 11
- [Python 3.10+](https://python.org) (make sure to check **"Add Python to PATH"** during installation)
- [Git](https://git-scm.com/)

---

## Installation

Run this command in **PowerShell (Admin)**:

```powershell
$repoPath = "C:\JupyterContext"; if (Test-Path $repoPath) { Remove-Item -Recurse -Force $repoPath }; git clone https://github.com/vikassharma545/Jupyter-Notebook.git $repoPath; cd $repoPath; Start-Process cmd.exe -ArgumentList "/c setup_context_menu.bat" -Verb RunAs
```

> **Note:** You can change `C:\JupyterContext` to any path you prefer. The installer automatically detects the install location — no hardcoded paths.

The installer will:
1. Check that Python and pip are available
2. Install Jupyter Notebook via pip
3. Verify the installation works
4. Add the right-click context menu to Windows Explorer

---

## Usage

- **Right-click on a folder** or **right-click on the desktop/folder background** and select **"Open with Jupyter"**
- Your default browser will open with the Jupyter interface
- A small Jupyter icon appears in the **system tray** (bottom-right, near clock)
- **Double-click** the tray icon to reopen the browser
- **Right-click** the tray icon and select **"Stop Server"** when done

---

## Uninstallation

To remove the context menu, run `uninstall.bat` as Administrator from the install directory:

```powershell
cd C:\JupyterContext
Start-Process cmd.exe -ArgumentList "/c uninstall.bat" -Verb RunAs
```

This will:
1. Remove the context menu entries from Windows Explorer
2. Optionally uninstall the Jupyter Notebook pip package

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Open with Jupyter" not appearing** | Restart Windows Explorer (or log out and back in) after installation |
| **"jupyter is not recognized"** | Python Scripts directory is not on PATH. Reinstall Python with "Add to PATH" checked |
| **Permission denied during setup** | Right-click PowerShell and select "Run as Administrator" |
| **Icon not showing in context menu** | Verify `jupyter.ico` exists in the install directory |
| **Folder paths with spaces fail** | This is fixed in the latest version. Re-run the installer to update |

---

## License

[MIT License](LICENSE) — Free to use and share!
