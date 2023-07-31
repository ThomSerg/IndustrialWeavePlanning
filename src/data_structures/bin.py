from dataclasses import dataclass

from cpmpy.expressions.variables import intvar

from src.data_structures.bin_config import BinConfig
from src.utils.fixable_object import FixableObject
import src.utils.fixable_type as ft


@dataclass(kw_only=True)
class Bin(FixableObject):

    '''
    A large object.
    '''

    config: BinConfig                       # configuration
    fixable_length: ft.FixableInt = None    # length

    def __post_init__(self):
        if self.fixable_length is None: self.fixable_length = ft.FixableInt(fixable_parent=self, free_value=intvar(self.config.min_length, self.config.max_length))

    # Properties

    def get_variables(self):
        return [self.length]

    @property
    def width(self) -> int:
        return self.config.width
    
    @property
    def length(self) -> ft.Int:
        return self.fixable_length.value()

    @property
    def max_length(self) -> int:
        return self.config.max_length
    
    @property
    def min_length(self) -> int:
        return self.config.min_length

    @property
    def area(self) -> intvar:
        return self.width*self.length
