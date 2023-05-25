from dataclasses import dataclass

# max aantal verschillende zones
# hoeveel zones er actief zijn
# configuratie van elke zone
# startpunt en lengte

from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname

import numpy as np
import numpy.typing as npt

from iterative.CompositeColor import CompositeColor
from iterative.data_structures.BasicColor import BasicColor
from iterative.creel.variables.CreelColorSection import CreelColorSection
from iterative.creel.variables.CreelConfig import CreelConfig

@dataclass(kw_only=True)
class CreelSection:

    _colors: list[BasicColor]           # The different basic colors to be provided by the creel
    _min_widths: npt.NDArray[np.int_]   # The smallest width for each section of each basic color creel config
    _creel_config: CreelConfig

    _creel_color_sections: list[CreelColorSection] = None

    def __post_init__(self):
        if self._creel_color_sections is None: self._creel_color_sections = self._creel_color_sections_var()



    @property
    def color_sections(self) -> list[CreelColorSection]:
        return self._creel_color_sections

    def _creel_color_sections_var(self):
        return [CreelColorSection(_color=c,_min_width=int(mw), _total_width=self._creel_config._total_width) for (c,mw) in zip(self._colors, self._min_widths)]