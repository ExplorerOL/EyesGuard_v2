import ctypes
import datetime


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint),
    ]


class UserActivityMonitor:
    def __init__(self, activity_timeout: datetime.timedelta = datetime.timedelta(seconds=60)):
        self._activity_timeout : datetime.timedelta = activity_timeout
        self._idle_time_offset : datetime.timedelta = datetime.timedelta(seconds=0)

    def __get_user_idle_time_from_os(self) -> datetime.timedelta:
        last_input_info = LASTINPUTINFO()
        last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))
        time_ms = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
        return  datetime.timedelta(milliseconds=time_ms)

    @property
    def is_user_active(self) -> bool:
        if self.__get_user_idle_time_from_os() - self._idle_time_offset > self._activity_timeout:
            return False
        else:
            return True

    def set_activity_offset(self):
        if not self.is_user_active:
            self._idle_time_offset = self.__get_user_idle_time_from_os()

    def reset_activity_offset(self):
        self._idle_time_offset = datetime.timedelta(seconds=0)
