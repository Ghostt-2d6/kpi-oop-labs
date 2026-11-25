import ctypes
from ctypes import wintypes
import time


class IpcConfig:
    LAB6_TITLE = "Lab6 - Менеджер об'єктів"
    OBJECT2_TITLE = "Object2 - Генератор даних"
    OBJECT3_TITLE = "Object3 - Графік y=f(x)"
    WM_CLOSE = 0x0010
    WM_COPYDATA = 0x004A
    WM_USER = 0x0400
    WM_OBJ2_READY = WM_USER + 101
    WM_OBJ3_DRAW = WM_USER + 102
    WM_OBJ3_READY = WM_USER + 103
    WM_OBJ_ERROR = WM_USER + 104
    COPYDATA_PARAMS_ID = 1001
    GWLP_WNDPROC = -4
    SW_RESTORE = 9
    HWND_TOP = 0
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040
    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002
    START_TIMEOUT_MS = 10000
    POLL_INTERVAL_MS = 100


class CopyDataStruct(ctypes.Structure):
    _fields_ = [
        ("dwData", ctypes.c_size_t),
        ("cbData", ctypes.c_uint32),
        ("lpData", ctypes.c_void_p),
    ]


class Win32Bridge:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.is_64bit = ctypes.sizeof(ctypes.c_void_p) == 8
        self.lresult_t = ctypes.c_ssize_t
        self.wparam_t = ctypes.c_size_t
        self.lparam_t = ctypes.c_ssize_t
        self.wndproc_t = ctypes.WINFUNCTYPE(
            self.lresult_t, ctypes.c_void_p, ctypes.c_uint, self.wparam_t, self.lparam_t
        )
        self._configure_signatures()

    def _configure_signatures(self):
        u = self.user32
        vp, ui, ci = ctypes.c_void_p, ctypes.c_uint, ctypes.c_int
        self._set_wnd_long = u.SetWindowLongPtrW if self.is_64bit else u.SetWindowLongW
        specs = [
            (u.GetParent, [vp], vp),
            (u.FindWindowW, [wintypes.LPCWSTR, wintypes.LPCWSTR], vp),
            (u.IsWindow, [vp], ci),
            (u.SendMessageW, [vp, ui, self.wparam_t, self.lparam_t], self.lresult_t),
            (u.PostMessageW, [vp, ui, self.wparam_t, self.lparam_t], ci),
            (u.CallWindowProcW, [vp, vp, ui, self.wparam_t, self.lparam_t], self.lresult_t),
            (u.ShowWindow, [vp, ci], ci),
            (u.SetWindowPos, [vp, vp, ci, ci, ci, ci, ui], ci),
            (self._set_wnd_long, [vp, ci, vp], vp),
        ]
        for func, args, res in specs:
            func.argtypes = args
            func.restype = res

    def get_toplevel_hwnd(self, widget):
        widget.update_idletasks()
        inner = widget.winfo_id()
        parent = self.user32.GetParent(inner)
        return int(parent) if parent else int(inner)

    def find_window(self, title):
        hwnd = self.user32.FindWindowW(None, title)
        return int(hwnd) if hwnd else 0

    def is_window_alive(self, hwnd):
        return bool(hwnd and self.user32.IsWindow(hwnd))

    def send_copydata(self, target_hwnd, sender_hwnd, data_id, payload_bytes):
        buf = ctypes.create_string_buffer(payload_bytes, len(payload_bytes))
        cds = CopyDataStruct(data_id, len(payload_bytes), ctypes.cast(buf, ctypes.c_void_p))
        return self.user32.SendMessageW(
            target_hwnd, IpcConfig.WM_COPYDATA, sender_hwnd, ctypes.addressof(cds)
        )

    def post_message(self, target_hwnd, message_id, wparam=0, lparam=0):
        return bool(self.user32.PostMessageW(target_hwnd, message_id, wparam, lparam))

    def arrange_window(self, hwnd, x, y, width, height):
        if not self.is_window_alive(hwnd):
            return
        self.user32.ShowWindow(hwnd, IpcConfig.SW_RESTORE)
        self.user32.SetWindowPos(
            hwnd, IpcConfig.HWND_TOP, int(x), int(y), int(width), int(height),
            IpcConfig.SWP_SHOWWINDOW | IpcConfig.SWP_NOACTIVATE,
        )

    def hook_window(self, hwnd, callback):
        c_cb = self.wndproc_t(callback)
        old_proc = self._set_wnd_long(
            hwnd, IpcConfig.GWLP_WNDPROC, ctypes.cast(c_cb, ctypes.c_void_p)
        )
        return old_proc, c_cb

    def unhook_window(self, hwnd, old_proc):
        if hwnd and old_proc:
            self._set_wnd_long(hwnd, IpcConfig.GWLP_WNDPROC, old_proc)

    def call_default_proc(self, old_proc, hwnd, msg, wparam, lparam):
        return self.user32.CallWindowProcW(old_proc, hwnd, msg, wparam, lparam)


class Win32Clipboard:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self._configure_signatures()

    def _configure_signatures(self):
        u, k = self.user32, self.kernel32
        vp, ui, ci, st = ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_size_t
        specs = [
            (u.IsClipboardFormatAvailable, [ui], ci),
            (u.OpenClipboard, [vp], ci),
            (u.EmptyClipboard, [], ci),
            (u.SetClipboardData, [ui, vp], vp),
            (u.GetClipboardData, [ui], vp),
            (u.CloseClipboard, [], ci),
            (k.GlobalAlloc, [ui, st], vp),
            (k.GlobalLock, [vp], vp),
            (k.GlobalUnlock, [vp], ci),
            (k.GlobalFree, [vp], vp),
        ]
        for func, args, res in specs:
            func.argtypes = args
            func.restype = res

    def _open_with_retry(self):
        for _ in range(15):
            if self.user32.OpenClipboard(None):
                return True
            time.sleep(0.02)
        return False

    def write_text(self, text):
        if not self._open_with_retry():
            return False
        try:
            self.user32.EmptyClipboard()
            encoded = text.encode("utf-16-le") + b"\x00\x00"
            h_mem = self.kernel32.GlobalAlloc(IpcConfig.GMEM_MOVEABLE, len(encoded))
            if not h_mem:
                return False
            ptr = self.kernel32.GlobalLock(h_mem)
            if not ptr:
                self.kernel32.GlobalFree(h_mem)
                return False
            try:
                ctypes.memmove(ptr, encoded, len(encoded))
            finally:
                self.kernel32.GlobalUnlock(h_mem)
            if not self.user32.SetClipboardData(IpcConfig.CF_UNICODETEXT, h_mem):
                self.kernel32.GlobalFree(h_mem)
                return False
            return True
        finally:
            self.user32.CloseClipboard()

    def read_text(self):
        if not self.user32.IsClipboardFormatAvailable(IpcConfig.CF_UNICODETEXT):
            return None
        if not self._open_with_retry():
            return None
        try:
            h_data = self.user32.GetClipboardData(IpcConfig.CF_UNICODETEXT)
            if not h_data:
                return None
            ptr = self.kernel32.GlobalLock(h_data)
            if not ptr:
                return None
            try:
                return ctypes.wstring_at(ptr)
            finally:
                self.kernel32.GlobalUnlock(h_data)
        finally:
            self.user32.CloseClipboard()