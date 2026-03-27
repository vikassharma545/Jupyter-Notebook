# Open with Jupyter (Windows Context Menu) — No Anaconda Needed

[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?logo=windows&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![No Anaconda](https://img.shields.io/badge/Anaconda-Not%20Required-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Right-click any folder and instantly launch **Jupyter Notebook** — no Anaconda, no terminal, no hassle.

<p align="center">
  <img src="jupyter.ico" alt="Jupyter Icon" width="80">
</p>

---

## Features

- **One-click launch** — Right-click any folder → "Open with Jupyter"
- **No terminal clutter** — Jupyter runs hidden with a clean system tray icon
- **Multiple folders** — Open Jupyter in different folders at the same time, each on its own port
- **Easy control** — Right-click the tray icon to restart or stop the server
- **Works everywhere** — No hardcoded paths, works on any Windows PC

---

## Requirements

- **Windows 10 or 11**
- **[Python 3.10+](https://python.org)** — check **"Add Python to PATH"** during install
- **[Git](https://git-scm.com/)**

---

## Installation

Open **PowerShell as Administrator** and paste:

```powershell
$repoPath = "C:\JupyterContext"; if (Test-Path $repoPath) { Remove-Item -Recurse -Force $repoPath }; git clone https://github.com/vikassharma545/Jupyter-Notebook.git $repoPath; cd $repoPath; Start-Process cmd.exe -ArgumentList "/c setup_context_menu.bat" -Verb RunAs
```

> You can change `C:\JupyterContext` to any folder you like.

That's it! The installer handles everything automatically.

---

## How to Use

1. **Right-click** any folder or desktop background
2. Click **"Open with Jupyter"**
3. Your browser opens with Jupyter — a small icon appears in the system tray (near clock)

| Action | How |
|--------|-----|
| Reopen browser | Double-click the tray icon |
| Restart server | Right-click tray icon → **Restart Server** |
| Stop server | Right-click tray icon → **Stop Server** |

> You can run **multiple Jupyter servers** at once — each folder gets its own tray icon and port (8888, 8889, ...).

---

## Uninstall

Open **PowerShell as Administrator** and paste:

```powershell
cd C:\JupyterContext; Start-Process cmd.exe -ArgumentList "/c uninstall.bat" -Verb RunAs
```

---

## License

[MIT License](LICENSE) — Free to use and share!
