import sys
import os
import subprocess
import threading
import webbrowser
import re
import logging
import atexit
from urllib.request import Request, urlopen
from PIL import Image
import pystray

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(SCRIPT_DIR, "jupyter_tray.log")


def setup_logging():
    """Configure logging BEFORE main() so crashes under pythonw are always captured."""
    try:
        if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > 1_000_000:
            open(LOG_PATH, "w").close()
    except OSError:
        pass
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s [PID %(process)d] %(message)s",
    )


def main():
    work_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    # Validate work directory exists
    if not os.path.isdir(work_dir):
        logging.error("Directory does not exist: %s", work_dir)
        return

    folder_name = os.path.basename(os.path.normpath(work_dir)) or "Root"
    logging.info("Starting Jupyter for folder: %s", work_dir)

    # --- Load tray icon ---
    icon_path = os.path.join(SCRIPT_DIR, "jupyter.ico")
    if not os.path.exists(icon_path):
        logging.error("jupyter.ico not found at %s", icon_path)
        return
    try:
        image = Image.open(icon_path)
    except Exception:
        logging.exception("Failed to load icon: %s", icon_path)
        return

    # --- Find jupyter.exe via Python install path (not PATH dependent) ---
    python_dir = os.path.dirname(sys.executable)
    scripts_dir = os.path.join(python_dir, "Scripts")
    jupyter_exe = os.path.join(scripts_dir, "jupyter.exe")
    if not os.path.exists(jupyter_exe):
        jupyter_exe = "jupyter"

    # --- Start Jupyter server (hidden, auto-assigns port if busy) ---
    def start_jupyter():
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        return subprocess.Popen(
            [jupyter_exe, "notebook", "--no-browser"],
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW,
            env=env,
        )

    try:
        proc = start_jupyter()
    except FileNotFoundError:
        logging.error("jupyter executable not found at %s", jupyter_exe)
        return

    logging.info("Jupyter process started (PID %d)", proc.pid)

    # --- Graceful shutdown via Jupyter API (same as browser Quit button) ---
    def shutdown_jupyter(p):
        """Shutdown Jupyter gracefully via POST /api/shutdown, fallback to taskkill."""
        if p.poll() is not None:
            return
        pid = p.pid

        # Try the Jupyter API first (how the browser Quit button works)
        try:
            from notebook.notebookapp import list_running_servers
            for server in list_running_servers():
                if server["pid"] == pid:
                    url = server["url"] + "api/shutdown"
                    token = server["token"]
                    req = Request(url, method="POST", data=b"")
                    req.add_header("Authorization", "token " + token)
                    urlopen(req, timeout=5)
                    logging.info("Sent /api/shutdown to PID %d", pid)
                    try:
                        p.wait(timeout=10)
                        logging.info("Jupyter (PID %d) shut down gracefully", pid)
                        return
                    except subprocess.TimeoutExpired:
                        logging.warning("Graceful shutdown timed out for PID %d", pid)
                    break
        except Exception:
            logging.exception("API shutdown failed for PID %d", pid)

        # Fallback: force kill entire process tree
        if p.poll() is None:
            logging.info("Force killing process tree (PID %d)", pid)
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    capture_output=True,
                )
            except Exception:
                p.kill()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass

    # --- Ensure cleanup on exit (covers crashes, logoff, etc.) ---
    def cleanup():
        shutdown_jupyter(proc)

    atexit.register(cleanup)

    # --- State shared across threads ---
    state = {"url": None, "port": None, "running": True}
    tray_ref = [None]

    # --- Read jupyter output to capture URL ---
    def read_output(target_proc):
        """Read stdout from a specific process instance."""
        try:
            for line in iter(target_proc.stdout.readline, b""):
                text = line.decode("utf-8", errors="ignore")
                if state["url"] is None:
                    match = re.search(r"(https?://\S+)", text)
                    if match:
                        url = match.group(1).rstrip(")?.,")
                        state["url"] = url
                        port_match = re.search(r":(\d+)", url)
                        if port_match:
                            state["port"] = port_match.group(1)
                        logging.info("Jupyter ready at %s", url)
                        if tray_ref[0]:
                            tray_ref[0].title = (
                                f"Jupyter - {folder_name} (port {state['port']})"
                            )
                        webbrowser.open(url)
        except Exception:
            logging.exception("Error reading jupyter output")

    # --- Monitor process health ---
    def monitor_process(target_proc):
        """Monitor a specific process instance for exit."""
        target_proc.wait()
        # Only update state if this is still the active process
        if target_proc is proc:
            state["running"] = False
            logging.info("Jupyter exited (code %d)", target_proc.returncode)
            if tray_ref[0]:
                tray_ref[0].title = f"Jupyter - {folder_name} (stopped)"

    threading.Thread(target=read_output, args=(proc,), daemon=True).start()
    threading.Thread(target=monitor_process, args=(proc,), daemon=True).start()

    # --- Tray menu actions ---
    def open_browser(icon, item):
        url = state["url"] or "http://localhost:8888"
        webbrowser.open(url)

    def restart_server(icon, item):
        nonlocal proc
        # Kill old server and all its children
        shutdown_jupyter(proc)
        # Start new server
        try:
            proc = start_jupyter()
            state["url"] = None
            state["port"] = None
            state["running"] = True
            icon.title = f"Jupyter - {folder_name} (restarting...)"
            logging.info("Jupyter restarted (PID %d)", proc.pid)
            threading.Thread(target=read_output, args=(proc,), daemon=True).start()
            threading.Thread(target=monitor_process, args=(proc,), daemon=True).start()
        except Exception:
            logging.exception("Failed to restart Jupyter")

    def stop_server(icon, item):
        cleanup()
        icon.stop()

    # --- Dynamic menu text ---
    def get_status(item):
        if state["running"]:
            port = state["port"] or "starting..."
            return f"Port: {port}"
        return "Server stopped"

    def is_running(item):
        return state["running"]

    # --- Build tray icon (unique name per instance using PID) ---
    menu = pystray.Menu(
        pystray.MenuItem("Open Jupyter", open_browser, default=True),
        pystray.MenuItem(get_status, None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Restart Server", restart_server, visible=is_running),
        pystray.MenuItem("Stop Server", stop_server),
    )

    tooltip = f"Jupyter - {folder_name} (starting...)"
    tray = pystray.Icon(
        f"Jupyter-{os.getpid()}",
        image,
        tooltip,
        menu,
    )
    tray_ref[0] = tray
    tray.run()


if __name__ == "__main__":
    setup_logging()
    try:
        main()
    except Exception:
        logging.exception("jupyter_tray.py crashed")
