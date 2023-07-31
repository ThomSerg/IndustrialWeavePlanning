from dataclasses import dataclass

from .creel_section import CreelSection
from src.data_structures.color.color import Color
from .creel_config import CreelConfig
from src.data_structures.machine_config import MachineConfig

from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname
from src.utils.cpm_extensions import intvar_1D

from src.utils.fixable_object import FixableObject
import src.utils.fixable_type as ft


@dataclass(kw_only=True)
class CreelPacking(FixableObject):

    '''
    Creel packing
    '''

    max_creel_number: int           # max number of creel sections
    max_deadline: int               # last deadline
    max_colors: int                 # max number of colours per dent
    colors: list[Color]             # yarn colours
    min_widths: list[int]           # dim_{t_c, min}, minimal interval width
    machine_config: MachineConfig   # weaving machine config

    fixable_count: ft.FixableInt = None         # number of used creel packings
    fixable_starts: NDVarArray[intvar] = None   # starts of creel packings
    fixable_ends: NDVarArray[intvar] = None     # ends of creel packings

    _creel_sections: list[CreelSection] = None  # creel sections

    def __post_init__(self):
        self.creel_config = CreelConfig(total_width = self.machine_config.width, max_colors=self.max_colors)
        if self.fixable_count is None: self.fixable_count = ft.FixableInt(fixable_parent=self, free_value=self._count_var())
        if self.fixable_starts is None: self.fixable_starts = ft.FixableIntArray(fixable_parent=self, free_value=self._starts_var())
        if self.fixable_ends is None: self.fixable_ends = ft.FixableIntArray(fixable_parent=self, free_value=self._ends_var())
        if self._creel_sections is None: self._creel_sections = self._creel_sections_var()

    # Properties

    @property
    def count(self) -> intvar:
        return self.fixable_count.value()

    @property
    def starts(self) -> NDVarArray[intvar]:
        return self.fixable_starts.value()

    @property
    def ends(self) -> NDVarArray[intvar]:
        return self.fixable_ends.value()

    @property
    def sections(self) -> list[CreelSection]:
        return self._creel_sections
    
    # Decision variables

    def _starts_var(self):
        return intvar_1D(0, self.max_deadline-1, self.max_creel_number)

    def _ends_var(self):
        return intvar_1D(0, self.max_deadline-1, self.max_creel_number)
    
    def _count_var(self):
        return intvar(0, self.max_creel_number)

    def _creel_sections_var(self):
        
        return [
                CreelSection(
                    colors = self.colors,
                    min_widths = self.min_widths,
                    creel_config = self.creel_config                
                    ) for i in range(self.max_creel_number)
                ]