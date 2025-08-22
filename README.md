# 🚀 Open with Jupyter (Windows Context Menu) — No Anaconda Needed

[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?logo=windows&logoColor=white)](#)
[![PowerShell](https://img.shields.io/badge/PowerShell-5%2B-5391FE?logo=powershell&logoColor=white)](#)
[![No Anaconda](https://img.shields.io/badge/Anaconda-Not%20Required-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Boost your workflow with a single right‑click! This project adds a “Open with Jupyter” entry to the Windows Explorer context menu so you can launch Jupyter Notebook directly in any folder—no Anaconda required.

---

## 🔧 Requirements

- Windows 10/11
- PowerShell 5+
- Git
- Python 3.10+ 

---

## 🔥 Installation 

1. Run the provided PowerShell command in Admin Mode to clone the repo and set up the context menu:

   ```
   $repoPath = "C:\JupyterContext"; if (Test-Path $repoPath) { Remove-Item -Recurse -Force $repoPath }; git clone https://github.com/vikassharma545/Jupyter-Notebook.git $repoPath; cd $repoPath; Start-Process cmd.exe -ArgumentList "/c setup_context_menu.bat" -Verb RunAs
   ```

## 🌈 Usage

- Right-click a folder or desktop, select "Open with Jupyter" to launch Jupyter Notebook.


## 📜 License
[MIT License](LICENSE) - Free to use and share!
