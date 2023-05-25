import numpy as np
import numpy.typing as npt
from abc import ABC, abstractmethod

from src.data_structures.machine_config import MachineConfig
from .problem import Problem
from src.data_structures.bin_config import BinConfig
from src.data_structures.deadline_counts import DeadlineCounts
from src.data_structures.po import ProductionSchedule

class MultiBinProblem(Problem):


    deadlines : npt.NDArray[np.int_]
    deadline_counts : npt.NDArray[np.int_]


    def __init__(self):
        pass

    def get_deadlines(self): 
        return self.deadlines

    def get_deadline_counts(self): 
        return self.deadline_counts

    def get_production_schedule(self):
        return ProductionSchedule(
            _items=self.get_items(), 
            _deadlines=self.get_deadlines(), 
            _requirements=DeadlineCounts(_counts=self.get_deadline_counts()), 
            _fullfilments=DeadlineCounts(_counts=np.zeros(shape=self.get_deadline_counts().shape))
        )
    
    def get_bin_config(self):
        machine_config = self.get_machine_config()
        items = self.get_items()

        return BinConfig(
            _width=machine_config.width,
            _min_length=machine_config.min_length, #temp_machine_config.min_length,
            _max_length=machine_config.max_length,
        )

  