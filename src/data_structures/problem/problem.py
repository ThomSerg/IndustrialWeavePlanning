import numpy as np
import numpy.typing as npt
from abc import ABCMeta, abstractmethod

import math

from src.data_structures.abstract_item_packing import AbstractItemPacking
from src.data_structures.machine_config import MachineConfig
from src.data_structures.item import Item

class Problem(metaclass=ABCMeta):

    name: str
    widths : npt.NDArray[np.int_]
    heights : npt.NDArray[np.int_]
    machine_width : int 
    machine_min_length : int
    machine_max_length : int

    def __init__(self):
        pass

    @property
    def nr_items(self):
        return len(self.widths)

    def get_machine_config(self):
        return MachineConfig(
            width=self.machine_width,
            min_length=self.machine_min_length, 
            max_length=self.machine_max_length
            )

    def get_items(self):
        return [Item(ID=i, width=self.widths[i], height=self.heights[i]) for i in range(self.nr_items)]
    
    def get_item_packing(self, ItemPacking):
        return [
            ItemPacking(
                    item=i, 
                    max_count=math.floor((self.machine_width*self.machine_max_length)/i.area),
                    bin_config=self.get_bin_config(),
                ) for i in self.get_items()
        ]
    def get_item_packing_rotated(self, ItemPacking):
        return [
            ItemPacking(
                    item=i, 
                    max_count=math.floor((self.machine_width*self.machine_max_length)/i.area),
                    bin_config=self.get_bin_config(),
                    rotation=True
                ) for i in self.get_items()
        ]
    @abstractmethod
    def get_bin_config(self): pass





  