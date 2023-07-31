from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from src.data_structures.color.color import Color
from .creel_color_section import CreelColorSection
from .creel_config import CreelConfig


@dataclass(kw_only=True)
class CreelSection:

    '''
    Creel sections.
    '''

    colors: list[Color]                 # the different basic colors to be provided by the creel
    min_widths: npt.NDArray[np.int_]    # the smallest width for each section of each basic color creel config
    creel_config: CreelConfig           # creel config

    creel_color_sections: list[CreelColorSection] = None    # colour sections

    def __post_init__(self):
        if self.creel_color_sections is None: self.creel_color_sections = self._creel_color_sections_var()

    # Properties

    @property
    def color_sections(self) -> list[CreelColorSection]:
        return self.creel_color_sections
    
    # Variables

    def _creel_color_sections_var(self):
        return [CreelColorSection(color=c,min_width=int(mw), total_width=self.creel_config.total_width) for (c,mw) in zip(self.colors, self.min_widths)]