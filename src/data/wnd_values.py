from dataclasses import dataclass


@dataclass
class WndSettingsValues:
    pass


@dataclass
class TryIconValues:
    tooltip_str: str = ""
    protection_status: str = ""


@dataclass
class WndStatusValues:
    remaining_time_str: str = ""
    remaining_time_pbar_value: float = 0
    protection_status: str = ""
    btn_change_protection_state_enabled: bool = True
    btn_take_break_enabled: bool = True


@dataclass
class WndSettingsValues:
    protection_status: str = ""


@dataclass
class WndBreakValues:
    remaining_time_str: str = ""
    remaining_time_pbar_value: float = 0
