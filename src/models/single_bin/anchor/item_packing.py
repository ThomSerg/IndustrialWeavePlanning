from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import math

from cpmpy.expressions.python_builtins import all, any, sum
from cpmpy.expressions.variables import NDVarArray, intvar, boolvar, cpm_array, _IntVarImpl
from src.utils.cpm_extensions import intvar_1D, intvar_2D

from src.data_structures.item import Item
from src.data_structures.bin_config import BinConfig
from src.utils.fixable_object import FixableObject
import src.utils.fixable_type as ft

from src.data_structures.abstract_item_packing import AbstractItemPacking

@dataclass(kw_only=True)
class ItemPacking(AbstractItemPacking):
    
    
    
    def get_variables(self):
        return list(self.pos_xs) + list(self.pos_ys) + [self.count] + [self.selected] + list(self.active)
            

    @property
    def rotations(self):
        return np.full((self.nr_length_repeats(), self.nr_width_repeats()), self.rotation)
    
    @property
    def width(self):
        return self.item.width if not self.rotation else self.item.height

    @property
    def widths_arr(self):
        return np.full((self.nr_length_repeats(), self.nr_width_repeats()), self.width)
    
    @property
    def widths(self):
        return self.widths_arr.flatten()
    
    @property
    def height(self):
        return self.item.height if not self.rotation else self.item.width

    @property
    def heights_arr(self):
        return np.full((self.nr_length_repeats(), self.nr_width_repeats()), self.height)
    
    @property
    def heights(self):
        return self.heights_arr.flatten()
    


    def nr_width_repeats(self):
        return math.floor(self.bin_config.width / self.width)

    def nr_length_repeats(self):
        return math.floor(self.bin_config.max_length / self.height)

    def length_repeats_lower(self):
        return 0#math.ceil((self.bin_config.min_length + 1 - self.height) / self.height)

    def length_repeats_upper(self):
        return math.floor((self.bin_config.max_length - self.height) / self.height) 

    @property
    def free_max_count(self):
        return self.nr_width_repeats()*self.nr_length_repeats()

    # def _pos_xs_var(self):
    #     return intvar_1D(0, self.bin_config.width - self.item.smallest_side, self.nr_width_repeats()*self.nr_length_repeats())

    # def _pos_ys_var(self):
    #     return intvar_1D(0, self.bin_config.max_length - self.item.smallest_side, self.nr_width_repeats()*self.nr_length_repeats())

    def _pos_xs_var(self):

        w_repeats = self.nr_width_repeats()
        l_repeats = self.nr_length_repeats()

        self.min_move_x = np.zeros((self.nr_length_repeats(), self.nr_width_repeats()), dtype=int)
        self.max_move_x = np.zeros((self.nr_length_repeats(), self.nr_width_repeats()), dtype=int)

    
        for x in range(w_repeats): 
            if x == 0 & x == w_repeats - 1: 
                self.max_move_x[:,x] = np.repeat(self.bin_config.width - self.width, l_repeats)
            elif x == 0:
                self.max_move_x[:,x] = np.repeat(self.width - 1, l_repeats)
            elif x == w_repeats - 1:
                self.min_move_x[:,x] = np.repeat(x*self.width, l_repeats)
                self.max_move_x[:,x] = np.repeat(self.bin_config.width - self.width, l_repeats)
            else:
                self.min_move_x[:,x] = np.repeat(x*self.width, l_repeats)
                self.max_move_x[:,x] = np.repeat((x+1)*self.width - 1, l_repeats)

            # self.min_move_x[:,x] = np.repeat(0, l_repeats)
            # self.max_move_x[:,x] = np.repeat(self.bin_config.width - self.width, l_repeats)

        
        return intvar_2D(self.min_move_x, self.max_move_x)


    def _pos_ys_var(self):

        w_repeats = self.nr_width_repeats()
        l_repeats = self.nr_length_repeats()

        self.min_move_y = np.zeros((self.nr_length_repeats(), self.nr_width_repeats()), dtype=int)
        self.max_move_y = np.zeros((self.nr_length_repeats(), self.nr_width_repeats()), dtype=int)

        for y in range(l_repeats):
      
            if y == 0 & y == l_repeats - 1: 
                self.max_move_y[y,:] = np.repeat(self.bin_config.max_length - self.height, w_repeats)   # TODO kan obv max packing zone
            elif y == 0:
                self.max_move_y[y,:] = np.repeat(self.height - 1, w_repeats)
            elif y == l_repeats - 1:
                self.min_move_y[y,:] = np.repeat(y*self.height, w_repeats)
                self.max_move_y[y,:] = np.repeat(self.bin_config.max_length - self.height, w_repeats)
            else:
                self.min_move_y[y,:] = np.repeat(y*self.height, w_repeats)
                self.max_move_y[y,:] = np.repeat((y+1)*self.height - 1, w_repeats)
            
            # self.min_move_y[y,:] = np.repeat(0, w_repeats)
            # self.max_move_y[y,:] = np.repeat(self.bin_config.max_length - self.height, w_repeats)

        return intvar_2D(self.min_move_y, self.max_move_y)


    def _count_var(self):
        return intvar(0, self.nr_width_repeats()*self.nr_length_repeats())

    def _active_var(self):
        return boolvar((self.length_repeats_upper()-self.length_repeats_lower()+1, self.nr_width_repeats()))
    

    def __eq__(self, other):
        if isinstance(other, ItemPacking):
            return (self.item == other.item) & (self.count == other.count)
        else:
            return False
