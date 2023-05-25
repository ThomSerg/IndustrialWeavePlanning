
from iterative.creel.variables.CreelPacking import CreelPacking
from .CreelSectionModel import CreelSectionModel

import itertools

from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname
from cpmpy.expressions.globalconstraints import Element

class CreelPackingModel:

    def __init__(self,
                    creel_packing: CreelPacking
                ):
        self.creel_packing = creel_packing

    def get_constraints(self):

        c = []


        # End must come after starts
        c.extend([end >= start for (start,end) in zip(self.creel_packing.starts, self.creel_packing.ends)])
        
        # Creels must cover entire range
        c.append(self.creel_packing.starts[0] == 0)
        #c.append(Element(self.creel_packing.ends, self.creel_packing.count-1) == self.creel_packing._max_deadline-1)
        #c.append(self.creel_packing.ends[0] == 10)

        # Start must follow on previous end
        for (i,j) in itertools.pairwise(range(self.creel_packing._max_creel_number)):
            c.append(
                (j < self.creel_packing.count).implies(
                    self.creel_packing.starts[j] == self.creel_packing.ends[i] + 1
                )
            )
        
        # Get constraints of creel sections
        self.creel_section_models = [CreelSectionModel(cs,self.creel_packing.creel_config) for cs in self.creel_packing.sections]
        for csm in self.creel_section_models:
            c.extend(csm.get_constraints())
        
        return c
       
