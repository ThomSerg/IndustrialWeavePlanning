from __future__ import annotations
from dataclasses import dataclass,  field

from cpmpy.expressions.variables import cpm_array

from src.data_structures.abstract_item_packing import AbstractItemPacking
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking


@dataclass(kw_only=True, eq=False)
class SingleBinPacking(AbstractSingleBinPacking):

    '''
    Packing of a single object
    '''

    _items: list[AbstractItemPacking]                                               # items to pack
    _items_rotated: list[AbstractItemPacking] = field(default_factory=lambda: [])   # rotated items to pack

    def items_rotated(self, rotation:bool) -> list[AbstractItemPacking]:
        return self._items if not rotation else self._items_rotated
    
    # Properties

    @property
    def items(self) -> list[AbstractItemPacking]:
        return self._items + self._items_rotated
    
    @property
    def items_unique(self) -> list[AbstractItemPacking]:
        return self._items

    @property
    def counts(self):
        return cpm_array([x.count + x_r.count for (x,x_r) in zip(self.items_rotated(False), self.items_rotated(True))])