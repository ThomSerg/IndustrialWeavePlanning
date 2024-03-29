import itertools

from ..data_structures.creel_packing import CreelPacking
from .creel_section_model import CreelSectionModel


class CreelPackingModel:

    def __init__(self,
                    creel_packing: CreelPacking
                ):
        self.creel_packing = creel_packing

    def get_constraints(self):

        c = []

        # End must come after starts
        c.extend([end >= start for (start,end) in zip(self.creel_packing.starts, self.creel_packing.ends)])
        
        # Start must follow on previous end
        for (i,j) in itertools.pairwise(range(self.creel_packing.max_creel_number)):
            c.append(
                (j < self.creel_packing.count).implies(
                    self.creel_packing.starts[j] == self.creel_packing.ends[i] + 1 + self.creel_packing.machine_config.creel_switch_penalty
                )
            )
        
        # Get constraints of creel sections
        self.creel_section_models = [CreelSectionModel(cs,self.creel_packing.creel_config) for cs in self.creel_packing.sections]
        for csm in self.creel_section_models:
            c.extend(csm.get_constraints())
        
        return c