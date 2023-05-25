from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union

from cpmpy.expressions.variables import boolvar, intvar, cpm_array
from cpmpy.expressions.python_builtins import all, any
#from cpmpy.expressions.globalconstraints import 

from src.data_structures.bin import Bin
from src.models.single_bin.baseline.item_packing import ItemPacking
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking

@dataclass(kw_only=True)
class SingleBinPacking(AbstractSingleBinPacking):

    _items: list[ItemPacking]

    @property
    def items(self) -> list[ItemPacking]:
        return self._items 

    @property
    def counts(self):
        return cpm_array([x.count for x in self.items])

    


   

    
