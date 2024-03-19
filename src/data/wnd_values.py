from dataclasses import dataclass


@dataclass
class WndSettingsValues:
    pass


@dataclass
class TryIconValues:
    tooltip_str: str = ""
    protection_status: str = ""
    suspended_status: bool = False


@dataclass
class WndStatusValues:
    remaining_time_str: str = ""
    remaining_time_pbar_value: float = 0
    protection_status: str = ""
    suspended_status: bool = False
    # btn_change_protection_state_enabled: bool = True
    # btn_take_break_enabled: bool = True


@dataclass
class WndSettingsValues:
    protection_status: str = ""
    suspended_status: bool = False


@dataclass
class WndBreakValues:
    remaining_time_str: str = ""
    remaining_time_pbar_value: float = 0
