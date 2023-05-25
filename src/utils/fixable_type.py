from dataclasses import dataclass
from abc import ABCMeta, abstractmethod

from typing import TypeVar, Generic, Union

import numpy as np
import numpy.typing as npt

from cpmpy.expressions.variables import NDVarArray, intvar, boolvar

from .fixable_object import FixableObject

Fixed = TypeVar("Fixed")
Free = TypeVar("Free")

FixedInt = np.int_
FreeInt = intvar
Int = Union[FixedInt, FreeInt]

FixedIntArray = npt.NDArray[FixedInt]
FreeIntArray = NDVarArray[FreeInt]
IntArray = Union[FixedIntArray, FreeIntArray]

FixedBool = np.bool_
FreeBool = boolvar
Bool = Union[FixedBool, FreeBool]

FixedBoolArray = npt.NDArray[FixedBool]
FreeBoolArray = NDVarArray[FreeBool]
BoolArray = Union[FixedBoolArray, FreeBoolArray]

@dataclass(kw_only=True)
class FixableType(Generic[Fixed, Free], metaclass=ABCMeta):

    fixable_parent: FixableObject
    fixed_value: Fixed = None
    free_value: Free = None
    fixed = False

    @abstractmethod
    def _fix_value(self, value): pass

    def fix(self):
        self.fixed = True
        self.fixed_value = self.fix_value(self.free_value.value())

    # def free(self):
    #     self.fixed = False
    
    # def set_fixed_value(self, f:Fixed):
    #     self.fixed_value = f
    #     self.fixed = True

    # def set_free_value(self, f:Free):
    #     self.free_value = f
    #     self.fixed = False

    def value(self):
        if self.fixable_parent.fixed:
            if (not self.fixed):
                self.fix()
            return self.fixed_value  
        else:
            return self.free_value
    
class FixableArray(metaclass=ABCMeta):
    @abstractmethod
    def flatten(self): pass


class FixableInt(FixableType[int, intvar]):

    def fix_value(self, value):
        return FixableInt._fix_value(value)
    
    def _fix_value(value):
        return int(value)

class FixableBool(FixableType[bool, boolvar]):
    def __init__(self, fixable_parent):
        super().__init__(fixable_parent=fixable_parent, free_value=boolvar())

    def fix_value(self, value):
        return FixableBool._fix_value(value)
    
    def _fix_value(value):
        return bool(value)

class FixableIntArray(FixableType[FixedIntArray, FreeIntArray], FixableArray):
    def flatten(self):
        return FixableIntArray(fixable_parent=self.fixable_parent, free_value=self.free_value.flatten())

    def fix_value(self, value):
        return FixableIntArray._fix_value(value)
    
    def _fix_value(value):
        a = np.full_like(value, 1)
        for x in range(value.shape[0]):
            if (len(value.shape) == 1):
                a[x] = FixableInt._fix_value(value[x])
            else:
                for y in range(value.shape[1]):
                    a[x,y] = FixableInt._fix_value(value[x,y])
        return a

class FixableBoolArray(FixableType[FixedBoolArray, FreeBoolArray], FixableArray):
    def flatten(self):
        return FixableBoolArray(fixable_parent=self.fixable_parent, free_value=self.free_value.flatten())
    
    def fix_value(self, value):
        return FixableBoolArray._fix_value(value)

    def _fix_value(value):
        a = np.full_like(value, 1)
        for x in range(value.shape[0]):
            if (len(value.shape) == 1):
                a[x] = FixableBool._fix_value(value[x])
            else:
                for y in range(value.shape[1]):
                    a[x,y] = FixableBool._fix_value(value[x,y])
        return a


