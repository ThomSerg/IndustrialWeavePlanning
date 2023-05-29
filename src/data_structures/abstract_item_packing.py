from __future__ import annotations
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod

import numpy as np
import numpy.typing as npt
import math

from cpmpy.expressions.python_builtins import all, any, sum
from cpmpy.expressions.variables import NDVarArray, intvar, boolvar, cpm_array, _IntVarImpl

from src.data_structures.item import Item
from src.data_structures.bin_config import BinConfig
from src.utils.fixable_object import FixableObject
import src.utils.fixable_type as ft


@dataclass(kw_only=True)
class AbstractItemPacking(FixableObject):

    item: Item = None
    bin_config: BinConfig = None
    rotation: bool = False
    max_count: int = 0

    fixable_pos_xs_arr: ft.FixableIntArray = None
    fixable_pos_ys_arr: ft.FixableIntArray = None

    fixable_count: ft.FixableInt = None
    fixable_selected: ft.FixableBool = None
    fixable_active: ft.FixableBoolArray = None

    def __post_init__(self):
        
        self.fixable_pos_xs_arr = ft.FixableIntArray(fixable_parent=self, free_value=self._pos_xs_var())   
        self.fixable_pos_ys_arr = ft.FixableIntArray(fixable_parent=self, free_value=self._pos_ys_var())
        self.fixable_count = ft.FixableInt(fixable_parent=self, free_value=self._count_var())
        self.fixable_selected = ft.FixableBool(fixable_parent=self)
        self.fixable_active = ft.FixableBoolArray(fixable_parent=self, free_value=self._active_var())


    @abstractmethod
    def _pos_xs_var(): pass

    @abstractmethod
    def _pos_ys_var(): pass

    @property
    def pos_xs_arr(self) -> ft.IntArray:
        return self.fixable_pos_xs_arr.value()
    
    @property
    def pos_ys_arr(self) -> ft.IntArray:
        return self.fixable_pos_ys_arr.value()

    @property
    def pos_xs(self) -> ft.IntArray:
        return self.pos_xs_arr.flatten()
    
    @property
    def pos_ys(self) -> ft.IntArray:
        return self.pos_ys_arr.flatten()
    
    @property
    @abstractmethod
    def rotations(self): pass
    
    @property
    @abstractmethod
    def widths(self): pass

    @property
    @abstractmethod
    def heights(self): pass

    @property
    def area(self):
        return self.item.area

    @abstractmethod
    def _count_var(): pass

    @property
    def count(self):
        return self.fixable_count.value()

    @abstractmethod
    def _active_var(): pass

    @property
    def active_arr(self):
        return self.fixable_active.value()
    
    @property
    def active(self):
        return self.active_arr.flatten()

    @property
    def selected(self) -> ft.Bool:
        return self.fixable_selected.value()

    def get_variables(self):
        return list(self.pos_xs) + list(self.pos_ys) + [self.count] + [self.selected] + list(self.active)

