from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass

from cpmpy.expressions.variables import intvar
from cpmpy.expressions.python_builtins import all as cpm_all

from src.data_structures.bin import Bin
from src.utils.fixable_object import FixableObject


@dataclass(kw_only=True)
class AbstractSingleBinPacking(FixableObject):

    '''
    Abstract class representing a packed (or to be packed) singular large object.
    '''

    bin: Bin    # The large object in which to pack

    def get_variables(self):
        res = self.bin.get_variables()
        for item in self.items:
            res += item.get_variables()
        return res

    # Properties

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
    
    # Post-fix operations

    def _post_fix(self):
        for item in self.items:
            item.fix()
        self.bin.fix()
        
    def _post_free(self):
        for item in self.items:
            item.free()
        self.bin.free()

    # Equality comparison
    
    def __eq__(self, other):
        if isinstance(other, AbstractSingleBinPacking):
            return cpm_all(self.counts == other.counts)
        else:
            return False