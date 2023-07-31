
from cpmpy.expressions.globalconstraints import Cumulative

from ..data_structures.creel_section import CreelSection
from ..data_structures.creel_config import CreelConfig
from .creel_color_section_model import CreelColorSectionModel


def flatten(l):
    return [item for sublist in l for item in sublist]

class CreelSectionModel:

    def __init__(self,
                    creel_section: CreelSection,
                    creel_config: CreelConfig,
                ):
        self.creel_section = creel_section
        self.creel_config = creel_config

    def get_constraints(self):
        c = []

        starts = flatten([ccs.starts for ccs in self.creel_section.color_sections])
        durations = flatten([ccs.widths for ccs in self.creel_section.color_sections])
        ends = flatten([ccs.ends for ccs in self.creel_section.color_sections])
        demand = flatten([[i < ccs.count for i in range(ccs.max_repeats)] for ccs in self.creel_section.color_sections])

        # Limit number of colors at each position
        c.append(Cumulative(starts, durations, ends, demand, self.creel_config.max_colors))
   
        # Get constraints of creel color sections
        self.creel_color_section_models = [CreelColorSectionModel(cs) for cs in self.creel_section.color_sections]
        for ccsm in self.creel_color_section_models:
            c.extend(ccsm.get_constraints())

        return c