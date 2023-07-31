from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from cpmpy.expressions.variables import cpm_array

from src.models.single_bin.baseline.item_packing import ItemPacking
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking


@dataclass(kw_only=True, eq=False)
class SingleBinPacking(AbstractSingleBinPacking):

    '''
    Packing of a single object
    '''

    _items: list[ItemPacking]   # items to pack

    @property
    def items(self) -> list[ItemPacking]:
        return self._items 
    
    @property
    def items_unique(self) -> list[ItemPacking]:
        return self._items 

    @property
    def counts(self):
        return cpm_array([x.count for x in self.items])

    def __eq__(self, other):
        return self.super() == other

    


   

    
