from dataclasses import dataclass

@dataclass(kw_only=True)
class CreelConfig:

    _total_width: int
    _max_colors: int
    