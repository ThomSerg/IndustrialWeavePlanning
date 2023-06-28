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

@dataclass(kw_only=True)
class AbstractSingleBinPacking(FixableObject):

    bin: Bin

    @property
    @abstractmethod
    def items(self): pass

    @property
    @abstractmethod
    def items_unique(self): pass

    @property
    @abstractmethod
    def counts(self): pass

    @property
    def density(self) -> intvar:
        return self.area / self.bin.area

    @property
    def area(self) -> intvar:
        return sum(item.count*item.area for item in self.items)
    
    def get_variables(self):
        res = self.bin.get_variables()
        for item in self.items:
            res += item.get_variables()
        return res
    
    def _post_fix(self):
        for item in self.items:
            item.fix()
        self.bin.fix()
        
    def _post_free(self):
        for item in self.items:
            item.free()
        self.bin.free()
    
    def __eq__(self, other):
        if isinstance(other, AbstractSingleBinPacking):
            return all(i == o for (i,o) in zip(self.items, other.items))
        else:
            return False