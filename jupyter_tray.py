import sys
import os
import subprocess
import threading
import webbrowser
import re
from PIL import Image
import pystray


def main():
    work_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load tray icon early so we fail fast if missing
    icon_path = os.path.join(script_dir, "jupyter.ico")
    if not os.path.exists(icon_path):
        subprocess.Popen(
            ["cmd", "/c", "echo", "ERROR: jupyter.ico not found", "&", "pause"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return
    image = Image.open(icon_path)

    # Start jupyter notebook completely hidden
    try:
        proc = subprocess.Popen(
            ["jupyter", "notebook", "--no-browser"],
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except FileNotFoundError:
        subprocess.Popen(
            ["cmd", "/c", "echo", "ERROR: jupyter not found on PATH", "&", "pause"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return

    # Capture jupyter URL from output
    jupyter_url = [None]

    def read_output():
        for line in iter(proc.stdout.readline, b""):
            text = line.decode("utf-8", errors="ignore")
            if jupyter_url[0] is None:
                match = re.search(r"(https?://\S+)", text)
                if match:
                    url = match.group(1).rstrip(")?.,")
                    jupyter_url[0] = url
                    webbrowser.open(url)

    threading.Thread(target=read_output, daemon=True).start()

    def open_browser(icon, item):
        url = jupyter_url[0] or "http://localhost:8888"
        webbrowser.open(url)

    def stop_server(icon, item):
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("Open Jupyter", open_browser, default=True),
        pystray.MenuItem("Stop Server", stop_server),
    )

    icon = pystray.Icon("Jupyter Notebook", image, "Jupyter Notebook", menu)
    icon.run()


if __name__ == "__main__":
    main()
