from dataclasses import dataclass

import math

from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname
from cpmpy.expressions.python_builtins import any

import iterative.data_structures.FixableType as ft
from iterative.data_structures.FixableObject import FixableObject
from iterative.data_structures.BasicColor import BasicColor

@dataclass(kw_only=True)
class CreelColorSection(FixableObject):

    _color: BasicColor
    _min_width: int
    _total_width: int
    _max_repeats: int = 0

    _count: ft.FixableInt = None
    _starts: ft.FixableIntArray = None
    _widths: ft.FixableIntArray = None

    def __post_init__(self):
        self._max_repeats = math.floor(self._total_width / self._min_width)
        if self._count is None: self._count = ft.FixableInt(_fixable_object=self, _free_value=intvar(0, self._max_repeats))
        if self._starts is None: self._starts = ft.FixableIntArray(_fixable_object=self, _free_value=self._starts_var()) # TODO: better bounds?
        if self._widths is None: self._widths = ft.FixableIntArray(_fixable_object=self, _free_value=self._widths_var())


    def _post_fix(self):
        pass
    
    def _post_free(self):
        pass


    @property
    def color(self) -> BasicColor:
        return self._color

    @property
    def count(self) -> ft.Int:
        return self._count.value

    @property
    def starts(self) -> ft.IntArray:
        return self._starts.value

    @property
    def widths(self) -> ft.IntArray:
        return self._widths.value
    
    @property
    def ends(self) -> ft.IntArray:
        return self.starts + self.widths

    def _starts_var(self) -> NDVarArray[intvar]:
        if self._max_repeats == 1:
            return cpm_array([intvar(0, self._total_width)])
        return intvar(0, self._total_width, self._max_repeats)

    def _widths_var(self) -> NDVarArray[intvar]:
        if self._max_repeats == 1:
            return cpm_array([intvar(self._min_width, self._total_width)])
        return intvar(self._min_width, self._total_width, self._max_repeats)


    def is_here(self, x1: ft.Int) -> boolvar:
        return any([(s <= x1) & (x1 < s + w) & (i < self.count) for i,(s,w) in enumerate(zip(self.starts,self.widths))]) # TODO mogelijks problemen met rendgevelveschilen tussen kleurzone uit textielpositie bepalen en overlap van kleurzones bepalen
       

    def is_here_2(self, x1: ft.Int, x2: ft.Int) -> boolvar:
        return any([(s <= x1) & (x2 <= s+w) & (i < self.count) for i,(s,w) in enumerate(zip(self.starts,self.widths))])

    def is_here_2_fixed(self, x1: ft.Int, x2: int) -> boolvar:
        return any([(s <= x1) & (int(x2) <= s+w ) & (i < self.count) for i,(s,w) in enumerate(zip(self.starts,self.widths))]) # & (i < self.count) 