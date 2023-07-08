
from ..data_structures.creel_color_section import CreelColorSection

import itertools

from cpmpy.expressions.globalconstraints import Element

class CreelColorSectionModel:

    def __init__(self,
                    creel_color_section: CreelColorSection
                ):
        self.creel_color_section = creel_color_section

    def get_constraints(self):
        c = []

        # All sections combined can not be wider than total width
        c.append(
            (self.creel_color_section.count > 0).implies(
                Element(self.creel_color_section.ends, self.creel_color_section.count-1) <= self.creel_color_section.total_width
            )
        )

        # Each section must come after the previous one
        for (i,j) in itertools.pairwise(range(self.creel_color_section.max_repeats)):
            c.append(
                (j < self.creel_color_section.count).implies(
                    self.creel_color_section.ends[i] < self.creel_color_section.starts[j]
                )
            )

        return c