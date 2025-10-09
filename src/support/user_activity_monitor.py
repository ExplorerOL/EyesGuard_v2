import ctypes
import datetime


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint),
    ]


class UserActivityMonitor:
    def __init__(self, activity_timeout_s: int = 10000):
        self._activity_timeout_dt : datetime.timedelta = datetime.timedelta(seconds=activity_timeout_s)
        self._last_activity_ts : datetime.datetime = datetime.datetime.now()

    def get_user_idle_time(self) -> datetime.timedelta:
        last_input_info = LASTINPUTINFO()
        last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))
        time_ms = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
        return datetime.timedelta(milliseconds=time_ms)

    @property
    def is_user_active(self) -> bool:
        if self.get_user_idle_time() > self._activity_timeout_dt:
            self._last_activity_ts = datetime.datetime.now()
            return False
        else:
            return True
