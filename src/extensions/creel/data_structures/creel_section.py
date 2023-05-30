from dataclasses import dataclass

from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname

import numpy as np
import numpy.typing as npt


from src.data_structures.color.color import Color
from .creel_color_section import CreelColorSection
from .creel_config import CreelConfig

@dataclass(kw_only=True)
class CreelSection:

    colors: list[Color]                 # The different basic colors to be provided by the creel
    min_widths: npt.NDArray[np.int_]    # The smallest width for each section of each basic color creel config
    creel_config: CreelConfig

    creel_color_sections: list[CreelColorSection] = None

    def __post_init__(self):
        if self.creel_color_sections is None: self.creel_color_sections = self._creel_color_sections_var()

    @property
    def color_sections(self) -> list[CreelColorSection]:
        return self.creel_color_sections

    def _creel_color_sections_var(self):
        return [CreelColorSection(color=c,min_width=int(mw), total_width=self.creel_config.total_width) for (c,mw) in zip(self.colors, self.min_widths)]