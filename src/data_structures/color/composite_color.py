from dataclasses import dataclass

from src.data_structures.color.color import Color


@dataclass()
class CompositeColor:

    '''
    Collection of multiple yarn colours.
    '''

    ID: int                     # identifier
    basic_colors: list[Color]   # yarn colours

    # Properties

    @property
    def hex(self) -> str:
        return self.basic_colors[0].hex

    