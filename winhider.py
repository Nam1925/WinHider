import win32gui  # pip install pywin32
import win32con
import keyboard  # pip install keyboard
import time
import json
import os

CONFIG_FILE = "config.json"

DEFAULT_KEYBINDS = {
    "toggle": "shift+tab",
    "exit": "shift+esc"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "hide_console": True,
            "show_on_exit": True,
            "keybind": DEFAULT_KEYBINDS
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config

    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        print("\033[91mWARN: Failed to read config.json. Using defaults.\033[0m")
        return {
            "hide_console": True,
            "run_on_startup": False,
            "keybind": DEFAULT_KEYBINDS
        }

# WINDOW FUNCTIONS
def enum_windows_callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title.strip():
            windows.append((hwnd, title))

def list_windows():
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows

def hide_from_taskbar(hwnd):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    style &= ~win32con.WS_EX_APPWINDOW
    style |= win32con.WS_EX_TOOLWINDOW
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

def show_again(hwnd):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    style &= ~win32con.WS_EX_TOOLWINDOW
    style |= win32con.WS_EX_APPWINDOW
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

# MAIN
def main():
    config = load_config()
    running = True
    hidden = False

    # Lime banner
    banner = r'''
██╗    ██╗██╗███╗   ██╗██╗  ██╗██╗██████╗ ███████╗██████╗ 
██║    ██║██║████╗  ██║██║  ██║██║██╔══██╗██╔════╝██╔══██╗
██║ █╗ ██║██║██╔██╗ ██║███████║██║██║  ██║█████╗  ██████╔╝
██║███╗██║██║██║╚██╗██║██╔══██║██║██║  ██║██╔══╝  ██╔══██╗
╚███╔███╔╝██║██║ ╚████║██║  ██║██║██████╔╝███████╗██║  ██║
 ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
'''
    print("\033[92m" + banner + "\033[0m")
    print("=> Make your window disappear from the taskbar and alt-tab list <=")
    print("By Nam1925\n")

    # ===== HOTKEYS =====
    toggle_key = config.get("keybind", {}).get("toggle", DEFAULT_KEYBINDS["toggle"])
    exit_key = config.get("keybind", {}).get("exit", DEFAULT_KEYBINDS["exit"])

    # Validate and register immediately
    try:
        keyboard.add_hotkey(toggle_key, lambda: None)
    except Exception:
        print(f"\033[91mWARN: Keybinds Error in toggle keybind: '{toggle_key}'. Using default '{DEFAULT_KEYBINDS['toggle']}'\033[0m")
        toggle_key = DEFAULT_KEYBINDS["toggle"]
    keyboard.add_hotkey(toggle_key, lambda: None)

    try:
        keyboard.add_hotkey(exit_key, lambda: None)
    except Exception:
        print(f"\033[91mWARN: Keybinds Error in exit keybind: '{exit_key}'. Using default '{DEFAULT_KEYBINDS['exit']}'\033[0m")
        exit_key = DEFAULT_KEYBINDS["exit"]
    keyboard.add_hotkey(exit_key, lambda: None)

    # ===== WINDOWS LIST =====
    windows = list_windows()
    print("\n[WINHIDER] Available windows:")
    for i, (hwnd, title) in enumerate(windows):
        print(f"{i}: {title} (HWND: {hwnd})")

    try:
        choice = int(input("\n[WINHIDER] Enter number of the window: "))
        hwnd, title = windows[choice]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return

    print(f"\n[WINHIDER] Selected window: {title}\n")

    if config.get("hide_console", True):
        hide_from_taskbar(windows[0][0])

    # ===== CALLBACKS =====
    def toggle_window():
        nonlocal hidden
        if hidden:
            show_again(hwnd)
            print(f"[WINHIDER] '{title}' shown")
            hidden = False
        else:
            hide_from_taskbar(hwnd)
            print(f"[WINHIDER] '{title}' hidden")
            hidden = True

    def exit_program():
        nonlocal running
        running = False
        if config.get("show_on_exit", "True"): 
            show_again(hwnd)
            print(f"[WINHIDER] Reshow '{title}'")
        print("\n[WINHIDER] Exiting...")

    # Re-register actual callbacks
    keyboard.clear_all_hotkeys()
    keyboard.add_hotkey(toggle_key, toggle_window)
    keyboard.add_hotkey(exit_key, exit_program)

    print(f"Press {toggle_key} to toggle hide/show.")
    print(f"Press {exit_key} to quit.\n")

    while running:
        time.sleep(0.1)

if __name__ == "__main__":
    main()
