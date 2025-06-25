# 🚀 Jupyter Notebook Context Menu

🌟 **Enhance your Workflow!** This repository contains scripts to add a "Open with Jupyter" context menu to Windows Explorer.

## 🔥 Installation 

1. Run the provided PowerShell command in Admin Mode to clone the repo and set up the context menu:

   ```
   $repoPath = "C:\JupyterContext"; if (Test-Path $repoPath) { Remove-Item -Recurse -Force $repoPath }; git clone https://github.com/vikassharma545/Jupyter-Notebook.git $repoPath; cd $repoPath; Start-Process cmd.exe -ArgumentList "/c setup_context_menu.bat" -Verb RunAs
   ```

## 🌈 Usage

- Right-click a folder or desktop, select "Open with Jupyter" to launch Jupyter Notebook.


## 📜 License
[MIT License](LICENSE) - Free to use and share!
