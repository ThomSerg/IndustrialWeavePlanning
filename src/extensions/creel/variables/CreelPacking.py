from dataclasses import dataclass

# max aantal verschillende zones
# hoeveel zones er actief zijn
# configuratie van elke zone
# startpunt en lengte

from .CreelSection import CreelSection
from iterative.data_structures.BasicColor import BasicColor
from .CreelConfig import CreelConfig
from iterative.data_structures.Machineconfig import MachineConfig

from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname

@dataclass(kw_only=True)
class CreelPacking:

    _max_creel_number: int
    _max_deadline: int
    _max_colors: int
    _colors: list[BasicColor] 
    _min_widths: list[int]
    _machine_config: MachineConfig

    _creel_count: intvar = None
    _creel_starts: NDVarArray[intvar] = None
    _creel_ends: NDVarArray[intvar] = None

    _creel_sections: list[CreelSection] = None

    def __post_init__(self):
        self.creel_config = CreelConfig(_total_width = self._machine_config.width, _max_colors=self._max_colors)
        if self._creel_count is None: self._creel_count = intvar(0, self._max_creel_number)
        if self._creel_starts is None: self._creel_starts = self._creel_starts_var()
        if self._creel_ends is None: self._creel_ends = self._creel_ends_var()
        if self._creel_sections is None: self._creel_sections = self._creel_sections_var()


    def _creel_starts_var(self):

        if self._max_creel_number == 1:
            return cpm_array([intvar(0, self._max_deadline-1)])
        return intvar(0, self._max_deadline-1, self._max_creel_number)

    def _creel_ends_var(self):
        if self._max_creel_number == 1:
            return cpm_array([intvar(0, self._max_deadline-1)])
        return intvar(0, self._max_deadline-1, self._max_creel_number)

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

    def _creel_sections_var(self):
        
        return [
            CreelSection(
                _colors=self._colors,
                _min_widths=self._min_widths,
                _creel_config=self.creel_config                
                ) for i in range(self._max_creel_number)
                ]
    



