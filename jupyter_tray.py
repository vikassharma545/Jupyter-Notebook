import sys
import os
import subprocess
import threading
import webbrowser
import re
import logging
import atexit
from PIL import Image
import pystray
from typing import Optional, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.environ.get("TEMP", "C:\\")), "JupyterContext")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "jupyter_tray.log")


def setup_logging() -> None:
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


def main() -> None:
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
    def start_jupyter() -> subprocess.Popen:
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

    # --- Graceful shutdown using Jupyter's own API ---
    def stop_jupyter(p: subprocess.Popen) -> None:
        """Shutdown Jupyter the same way the browser Quit button does."""
        if p.poll() is not None:
            return
        pid = p.pid

        # Use Jupyter's built-in shutdown (lazy import to avoid startup crash)
        try:
            from notebook.notebookapp import list_running_servers, shutdown_server
            for server in list_running_servers():
                if server["pid"] == pid:
                    stopped = shutdown_server(server, timeout=10)
                    if stopped or p.poll() is not None:
                        logging.info("Jupyter (PID %d) shut down gracefully", pid)
                        return
                    break
        except ImportError:
            logging.warning("notebook package not found, using force kill")
        except Exception:
            logging.exception("Graceful shutdown failed for PID %d", pid)

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
    def cleanup() -> None:
        stop_jupyter(proc)

    atexit.register(cleanup)

    # --- State shared across threads ---
    # user_action: True when Stop/Restart was clicked by user.
    #   Prevents monitor_process from auto-removing the tray icon
    #   when the server dies because WE told it to.
    #   Only False = server exited on its own (browser Quit) → auto-remove icon.
    state = {"url": None, "port": None, "running": True, "user_action": False}
    tray_ref = [None]

    # --- Read jupyter output to capture URL ---
    def read_output(target_proc: subprocess.Popen) -> None:
        """Read stdout from a specific process instance."""
        try:
            for line in iter(target_proc.stdout.readline, b""):
                text = line.decode("utf-8", errors="ignore")
                if state["url"] is None:
                    match = re.search(
                        r"(https?://(?:localhost|127\.0\.0\.1)\S+)", text
                    )
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
    def monitor_process(target_proc: subprocess.Popen) -> None:
        """Monitor a specific process instance for exit."""
        target_proc.wait()
        if target_proc is proc:
            state["running"] = False
            logging.info("Jupyter exited (code %d)", target_proc.returncode)
            # Auto-remove tray icon ONLY if server exited on its own
            # (e.g. browser Quit button). Don't remove during Stop/Restart.
            if not state["user_action"] and tray_ref[0]:
                tray_ref[0].stop()

    threading.Thread(target=read_output, args=(proc,), daemon=True).start()
    threading.Thread(target=monitor_process, args=(proc,), daemon=True).start()

    # --- Tray menu actions ---
    def open_browser(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        url = state["url"] or "http://localhost:8888"
        webbrowser.open(url)

    def restart_server(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Restart in a background thread so the tray icon stays responsive."""
        def do_restart() -> None:
            nonlocal proc
            state["user_action"] = True
            stop_jupyter(proc)
            try:
                proc = start_jupyter()
                state["url"] = None
                state["port"] = None
                state["running"] = True
                state["user_action"] = False
                icon.title = f"Jupyter - {folder_name} (restarting...)"
                logging.info("Jupyter restarted (PID %d)", proc.pid)
                threading.Thread(
                    target=read_output, args=(proc,), daemon=True
                ).start()
                threading.Thread(
                    target=monitor_process, args=(proc,), daemon=True
                ).start()
            except Exception:
                state["user_action"] = False
                logging.exception("Failed to restart Jupyter")
        threading.Thread(target=do_restart, daemon=True).start()

    def stop_server(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Stop in a background thread so the tray icon stays responsive."""
        def do_stop() -> None:
            state["user_action"] = True
            cleanup()
            icon.stop()
        threading.Thread(target=do_stop, daemon=True).start()

    # --- Dynamic menu text ---
    def get_status(item: pystray.MenuItem) -> str:
        if state["running"]:
            port = state["port"] or "starting..."
            return f"Port: {port}"
        return "Server stopped"

    def is_running(item: pystray.MenuItem) -> bool:
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
