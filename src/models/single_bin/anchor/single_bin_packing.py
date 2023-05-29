from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass,  field
from typing import Union
import math

from cpmpy.expressions.variables import boolvar, intvar, cpm_array
from cpmpy.expressions.python_builtins import all, any
#from cpmpy.expressions.globalconstraints import 

from src.data_structures.bin import Bin
from src.data_structures.abstract_item_packing import AbstractItemPacking

import numpy as np
import numpy.typing as npt


from src.utils.fixable_object import FixableObject
import src.utils.fixable_type as ft

from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking

@dataclass(kw_only=True, eq=False)
class SingleBinPacking(AbstractSingleBinPacking):

    _items: list[AbstractItemPacking]
    _items_rotated: list[AbstractItemPacking] = field(default_factory=lambda: [])

    def items_rotated(self, rotation:bool) -> list[AbstractItemPacking]:
        return self._items if not rotation else self._items_rotated

    @property
    def items(self) -> list[AbstractItemPacking]:
        return self._items + self._items_rotated
    
    @property
    def items_unique(self) -> list[AbstractItemPacking]:
        return self._items

    @property
    def counts(self):
        return cpm_array([x.count + x_r.count for (x,x_r) in zip(self.items_rotated(False), self.items_rotated(True))])
    

        


    

    
