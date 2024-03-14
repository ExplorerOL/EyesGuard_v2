from dataclasses import dataclass


@dataclass
class WndSettingsValues:
    pass


@dataclass
class TryIconValues:
    tooltip_str: str = ""


@dataclass
class WndStatusValues:
    remaining_time_str: str = ""
    remaining_time_pbar_value: float = 0
