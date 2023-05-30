from dataclasses import dataclass

@dataclass(kw_only=True)
class CreelConfig:

    total_width: int
    max_colors: int
    