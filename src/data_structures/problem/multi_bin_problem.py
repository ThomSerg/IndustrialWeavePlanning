import numpy as np
import numpy.typing as npt

from .problem import Problem
from src.data_structures.bin_config import BinConfig
from src.data_structures.deadline_counts import DeadlineCounts
from src.data_structures.production_schedule import ProductionSchedule


class MultiBinProblem(Problem):

    '''
    Single Large Object Placement Problem (SLOPP) + Due dates
    '''

    deadlines : npt.NDArray[np.int_]        # due dates
    deadline_counts : npt.NDArray[np.int_]  # demands


    def __init__(self):
        pass

    def get_deadlines(self): 
        return self.deadlines

    def get_deadline_counts(self): 
        return self.deadline_counts

    def get_production_schedule(self):
        return ProductionSchedule(
            items = self.get_items(), 
            deadlines = self.get_deadlines(), 
            requirements = DeadlineCounts(counts=self.get_deadline_counts()), 
            fullfilments = DeadlineCounts(counts=np.zeros(shape=self.get_deadline_counts().shape))
        )
    
    def get_bin_config(self):
        machine_config = self.get_machine_config()

        return BinConfig(
            width=machine_config.width,
            min_length=machine_config.min_length,
            max_length=machine_config.max_length,
        )