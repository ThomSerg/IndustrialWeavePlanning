from dataclasses import dataclass

import math

from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname
from cpmpy.expressions.python_builtins import any as cpm_any
from cpmpy.expressions.python_builtins import all as cpm_all
from src.utils.cpm_extensions import intvar_1D

import src.utils.fixable_type as ft
from src.utils.fixable_object import FixableObject
from src.data_structures.color.color import Color

@dataclass(kw_only=True)
class CreelColorSection(FixableObject):

    color: Color
    min_width: int
    total_width: int
    max_repeats: int = 0

    fixable_count: ft.FixableInt = None
    fixable_starts: ft.FixableIntArray = None
    fixable_widths: ft.FixableIntArray = None

    def __post_init__(self):
        self.max_repeats = math.floor(self.total_width / self.min_width)
        if self.fixable_count is None: self.fixable_count = ft.FixableInt(fixable_parent=self, free_value=intvar(0, self.max_repeats))
        if self.fixable_starts is None: self.fixable_starts = ft.FixableIntArray(fixable_parent=self, free_value=self._starts_var()) # TODO: better bounds?
        if self.fixable_widths is None: self.fixable_widths = ft.FixableIntArray(fixable_parent=self, free_value=self._widths_var())

    @property
    def count(self) -> ft.Int:
        return self.fixable_count.value()

    @property
    def starts(self) -> ft.IntArray:
        return self.fixable_starts.value()

    @property
    def widths(self) -> ft.IntArray:
        return self.fixable_widths.value()
    
    @property
    def ends(self) -> ft.IntArray:
        return self.starts + self.widths

    def _starts_var(self) -> NDVarArray[intvar]:
        res = []
        for i_repeat in range(self.max_repeats):
            res.append(intvar(self.min_width*i_repeat, self.min_width*(i_repeat+1)))
        #return intvar_1D(0, self.total_width-self.min_width, self.max_repeats)
        return cpm_array(res)

    def _widths_var(self) -> NDVarArray[intvar]:
        return intvar_1D(self.min_width, self.total_width, self.max_repeats)

    def is_here(self, x1: ft.Int) -> boolvar:
        return cpm_any([(s <= x1) & (x1 < s + w) & (i < self.count) for i,(s,w) in enumerate(zip(self.starts,self.widths))]) # TODO mogelijks problemen met rendgevelveschilen tussen kleurzone uit textielpositie bepalen en overlap van kleurzones bepalen
       

    def is_here_2(self, x1: ft.Int, x2: ft.Int) -> boolvar:
        return cpm_any([ cpm_all([(s <= x1), (x2 <= s+w), (i < self.count)]) for i,(s,w) in enumerate(zip(self.starts,self.widths))])

    def is_here_2_fixed(self, x1: ft.Int, x2: int) -> boolvar:
        return cpm_any([(s <= x1) & (int(x2) <= s+w ) & (i < self.count) for i,(s,w) in enumerate(zip(self.starts,self.widths))]) # & (i < self.count) 