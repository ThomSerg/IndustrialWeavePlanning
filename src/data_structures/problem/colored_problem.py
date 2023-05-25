import numpy as np
import numpy.typing as npt
from abc import ABC, abstractmethod

from src.data_structures.machine_config import MachineConfig
from src.data_structures.problem.problem import Problem
from src.data_structures.textile_item import TextileItem

from src.data_structures.color.color_collection import ColorCollection

class ColoredProblem(ABC, Problem):

    colors : npt.NDArray[np.int_]
    color_collection : ColorCollection
    max_creel_number: int
    max_creel_colors: int
    creel_switch_penalty: int

    def __init__(self):
        pass

    def get_machine_config(self):
        return MachineConfig(
            width=self.machine_width,
            min_length=self.machine_min_length, 
            max_length=self.machine_max_length,
            max_creel_number=self.max_creel_number,
            max_creel_colors=self.max_creel_colors,
            creel_switch_penalty=self.creel_switch_penalty
            )
    
    def get_items(self):
        return [TextileItem(ID=i, width=self.widths[i], height=self.heights[i], color=self.color_collection.get_color(self.colors[i]-1)) for i in range(self.nr_items)]
  