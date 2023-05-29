from dataclasses import dataclass

import numpy.typing as npt

from src.data_structures.deadline_counts import DeadlineCounts
from src.data_structures.item import Item

from dataclass_wizard import JSONWizard

@dataclass
class ProductionSchedule(JSONWizard):

    items: list[Item]

    deadlines: npt.NDArray

    requirements: DeadlineCounts
    fullfilments: DeadlineCounts 

    def get_requirements(self):
        return self.requirements.counts

    def get_requirements_for(self, deadline):
        return self.requirements.get_counts_for(deadline)

    def get_requirements_untill(self, deadline):
        return self.requirements.get_counts_untill(deadline)

    def get_fullfilments(self):
        return self.fullfilments.counts

    def get_fullfilments_for(self, deadline):
        return self.fullfilments.get_counts_for(deadline)

    def get_fullfilments_untill(self, deadline):
        return self.fullfilments.get_counts_untill(deadline)