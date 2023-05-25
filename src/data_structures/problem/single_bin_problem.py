from abc import ABC, abstractmethod

import numpy as np
import numpy.typing as npt

from src.data_structures.machine_config import MachineConfig
from .problem import Problem
from src.data_structures.bin_config import BinConfig

class SingleBinProblem(ABC, Problem):

    counts : npt.NDArray[np.int_]

    def __init__(self):
        pass


    def get_bin_config(self):
        machine_config = self.get_machine_config()
        items = self.get_items()

        return BinConfig(
            width=machine_config.width,
            min_length=machine_config.min_length, 
            max_length=machine_config.max_length,
        )



    

