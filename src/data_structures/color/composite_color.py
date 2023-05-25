from dataclasses import dataclass

from src.data_structures.color.color import Color

@dataclass()
class CompositeColor:

    ID: int
    basic_colors: list[Color]

    @property
    def hex(self) -> str:
        return self.basic_colors[0].hex

    