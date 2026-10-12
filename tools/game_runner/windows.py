"""PID/HWND-bound Windows console input and exact owned-process cleanup."""
import ctypes
import os
import subprocess
import time
from ctypes import wintypes


class FocusError(RuntimeError):
    pass


def validate_foreground(expected_hwnd, expected_pid, actual_hwnd, actual_pid):
    if not expected_hwnd or (expected_hwnd, expected_pid) != (actual_hwnd, actual_pid):
        raise FocusError("CK3 lost foreground or window ownership")


class WindowsBackend:
    def __init__(self, config):
        if os.name != "nt":
            raise RuntimeError("Game input requires Windows")
        self.config = config
        self.process = None
        self.started_pids = []
        self.hwnd = 0
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.user32.GetForegroundWindow.restype = wintypes.HWND
        self.user32.SetForegroundWindow.argtypes = [wintypes.HWND]
        self.user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self.user32.IsWindowVisible.argtypes = [wintypes.HWND]
        self.user32.IsWindowVisible.restype = wintypes.BOOL
        self.user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.user32.GetClientRect.restype = wintypes.BOOL
        self.user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
        self.user32.ClientToScreen.restype = wintypes.BOOL
        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        self.user32.SetForegroundWindow.restype = wintypes.BOOL
        self.user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
        self.user32.MapVirtualKeyW.restype = wintypes.UINT
        self.user32.SetProcessDPIAware()

    def start(self, save_name):
        if self.process:
            raise RuntimeError("Owned process already exists")
        try:
            listing = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ck3.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True, check=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.TimeoutExpired as error:
            raise TimeoutError("Windows process inventory timed out") from error
        except subprocess.CalledProcessError as error:
            raise RuntimeError("Windows process inventory failed") from error
        if '"ck3.exe"' in listing.stdout.lower():
            raise RuntimeError("An unrelated CK3 process is running; refusing adoption")
        args = [str(self.config.game_executable), "-debug_mode", "-suppress_error_log", "-skip_checksum", "-disable_ai", "-loadsave=" + save_name]
        self.process = subprocess.Popen(args, cwd=self.config.game_executable.parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.started_pids.append(self.process.pid)
        deadline = time.monotonic() + self.config.startup_timeout
        callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError("Owned CK3 exited during startup")
            handles = []
            def find(hwnd, _):
                pid = wintypes.DWORD()
                self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if pid.value == self.process.pid and self.user32.IsWindowVisible(hwnd):
                    handles.append(hwnd)
                return True
            callback = callback_type(find)
            self.user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
            self.user32.EnumWindows.restype = wintypes.BOOL
            self.user32.EnumWindows(callback, 0)
            if handles:
                self.hwnd = handles[0]
                self.user32.SetForegroundWindow(self.hwnd)
                self.validate()
                return
            time.sleep(0.2)
        raise TimeoutError("CK3 window startup timed out")

    def validate(self):
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("Owned CK3 process is not alive")
        foreground = self.user32.GetForegroundWindow()
        pid = wintypes.DWORD()
        self.user32.GetWindowThreadProcessId(foreground, ctypes.byref(pid))
        validate_foreground(self.hwnd, self.process.pid, foreground, pid.value)

    def _input(self, vk=0, char=0, flags=0, release=False):
        if not release:
            self.validate()
        class Mouse(ctypes.Structure):
            _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("data", wintypes.DWORD), ("flags", wintypes.DWORD), ("time", wintypes.DWORD), ("extra", ctypes.c_size_t)]
        class Key(ctypes.Structure):
            _fields_ = [("vk", wintypes.WORD), ("scan", wintypes.WORD), ("flags", wintypes.DWORD), ("time", wintypes.DWORD), ("extra", ctypes.c_size_t)]
        class Payload(ctypes.Union):
            _fields_ = [("mouse", Mouse), ("key", Key)]
        class Input(ctypes.Structure):
            _fields_ = [("type", wintypes.DWORD), ("payload", Payload)]
        scan = char if char else self.user32.MapVirtualKeyW(vk, 0)
        key = Key(vk, scan, flags, 0, 0)
        event = Input(1, Payload(key=key))
        self.user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(Input), ctypes.c_int]
        self.user32.SendInput.restype = wintypes.UINT
        if self.user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(event)) != 1:
            raise RuntimeError("Windows rejected game input")

    def key(self, vk):
        self._input(vk)
        try:
            self.validate()
        finally:
            self._input(vk, flags=2, release=True)
        time.sleep(0.08)

    def open_console(self):
        self.key(0xC0)
        time.sleep(0.2)

    def command(self, text):
        self.validate()
        self._input(0x11)
        try:
            self.key(0x41)
        finally:
            # Key-up only releases our modifier, including after foreground loss.
            self._input(0x11, flags=2, release=True)
        self.key(0x08)
        for char in text:
            self._input(char=ord(char), flags=4)
            try:
                self.validate()
            finally:
                self._input(char=ord(char), flags=6, release=True)
        self.key(0x0D)
        time.sleep(0.1)

    def screenshot(self, path):
        self.validate()
        # Optional evidence capture; transport does not depend on Pillow.
        from PIL import ImageGrab
        rect, point = wintypes.RECT(), wintypes.POINT()
        self.user32.GetClientRect(self.hwnd, ctypes.byref(rect))
        self.user32.ClientToScreen(self.hwnd, ctypes.byref(point))
        ImageGrab.grab(bbox=(point.x, point.y, point.x + rect.right, point.y + rect.bottom)).save(path)

    def stop(self):
        process = self.process
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=15)
            self.process, self.hwnd = None, 0
