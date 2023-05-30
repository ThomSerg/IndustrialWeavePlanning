from dataclasses import dataclass

from .creel_section import CreelSection
from src.data_structures.color import Color
from .creel_config import CreelConfig
from src.data_structures.machine_config import MachineConfig

from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname
from src.utils.cpm_extensions import intvar_1D

from src.utils.fixable_object import FixableObject
import src.utils.fixable_type as ft


@dataclass(kw_only=True)
class CreelPacking(FixableObject):

    max_creel_number: int
    max_deadline: int
    max_colors: int
    colors: list[Color] 
    min_widths: list[int]
    machine_config: MachineConfig

    fixable_count: ft.FixableInt = None
    fixable_starts: NDVarArray[intvar] = None
    fixable_ends: NDVarArray[intvar] = None

    _creel_sections: list[CreelSection] = None

    def __post_init__(self):
        self.creel_config = CreelConfig(total_width = self.machine_config.width, max_colors=self.max_colors)
        if self.fixable_count is None: self.fixable_count = ft.FixableInt(fixable_parent=self, free_value=self._count_var())
        if self.fixable_starts is None: self.fixable_starts = ft.FixableIntArray(fixable_parent=self, free_value=self._starts_var())
        if self.fixable_ends is None: self.fixable_ends = ft.FixableIntArray(fixable_parent=self, free_value=self._ends_var())
        if self._creel_sections is None: self._creel_sections = self._creel_sections_var()

    @property
    def count(self) -> intvar:
        return self._creel_count

    @property
    def starts(self) -> NDVarArray[intvar]:
        return self._creel_starts

    @property
    def ends(self) -> NDVarArray[intvar]:
        return self._creel_ends

    @property
    def sections(self) -> list[CreelSection]:
        return self._creel_sections
    
    def _starts_var(self):
        return intvar_1D(0, self.max_deadline-1, self.max_creel_number)

    def _ends_var(self):
        return intvar_1D(0, self.max_deadline-1, self.max_creel_number)
    
    def _count_var(self):
        return intvar(0, self._max_creel_number)

    def _creel_sections_var(self):
        
        return [
                CreelSection(
                    colors=self.colors,
                    min_widths=self.min_widths,
                    creel_config=self.creel_config                
                    ) for i in range(self.max_creel_number)
                ]
    
    
    



