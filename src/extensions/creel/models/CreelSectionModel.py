
from ..variables import CreelSection, CreelConfig
from .CreelColorSectionModel import CreelColorSectionModel

class CreelSectionModel:

    def __init__(self,
                    creel_section: CreelSection,
                    creel_config: CreelConfig,
                ):
        self.creel_section = creel_section
        self.creel_config = creel_config

    def get_constraints(self):
        c = []

        # Limit number of colors at each position
        for ccs in self.creel_section.color_sections:
            for (i,start) in enumerate(ccs.starts):
                c.append(
                    (i < ccs.count).implies(
                        sum([ccs2.is_here(start) for ccs2 in self.creel_section.color_sections if ccs2 != ccs]) < self.creel_config._max_colors
                    )
                )
   
        # Get constraints of creel color sections
        self.creel_color_section_models = [CreelColorSectionModel(cs) for cs in self.creel_section.color_sections]
        for ccsm in self.creel_color_section_models:
            c.extend(ccsm.get_constraints())

        return c