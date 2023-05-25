from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import math

from cpmpy.expressions.python_builtins import all, any, sum
from cpmpy.expressions.variables import NDVarArray, intvar, boolvar, cpm_array, _IntVarImpl

from src.data_structures.item import Item
from src.data_structures.bin_config import BinConfig
from src.utils.fixable_object import FixableObject
import src.utils.fixable_type as ft

from src.data_structures.abstract_item_packing import AbstractItemPacking

@dataclass(kw_only=True)
class ItemPacking(AbstractItemPacking):
    
    rotation: bool = False
    
    def get_variables(self):
        return list(self.free_pos_xs) + list(self.free_pos_ys) + [self.free_count] + [self.selected] + list(self.free_active)
            



    @property
    def width(self):
        return self.item.width if not self.rotation else self.item.height
    
    @property
    def height(self):
        return self.item.height if not self.rotation else self.item.width

    def nr_width_repeats(self):
        return math.floor(self.bin_config.width / self.width)

    def nr_length_repeats(self):
        return math.floor(self.bin_config.max_length / self.height)

    def length_repeats_lower(self):
        return math.ceil((self.bin_config.min_packing_zone + 1 - self.height) / self.height)

    def length_repeats_upper(self):
        return math.floor((self.bin_config.max_packing_zone - self.height) / self.height) 

    @property
    def free_max_count(self):
        return self.nr_width_repeats()*self.nr_length_repeats()

    def _pos_xs_var(self):
        w_repeats = self.nr_width_repeats()
        vars = []

        self.min_move_x = np.zeros((self.length_repeats_upper()+1, self.nr_width_repeats()), dtype=int) # TODO beetje wastefull, maar anders met lelijke offsets moeten werken
        self.max_move_x = np.zeros((self.length_repeats_upper()+1, self.nr_width_repeats()), dtype=int)

        for y in range(self.length_repeats_lower(),self.length_repeats_upper()+1):
            temp_vars = []
            for x in range(w_repeats): # TODO is voor elke y steeds hetzelfde, kan berekening hergebruiken
                if x == 0 & x == w_repeats - 1: 
                    self.max_move_x[y,x] = self.bin_config.width - self.width
                elif x == 0:
                    self.max_move_x[y,x] = self.width - 1
                elif x == w_repeats - 1:
                    self.min_move_x[y,x] = x*self.width
                    self.max_move_x[y,x] = self.bin_config.width - self.width
                else:
                    self.min_move_x[y,x] = x*self.width
                    self.max_move_x[y,x] = (x+1)*self.width - 1
                
                temp_vars.append(intvar(self.min_move_x[y,x], self.max_move_x[y,x])) 

            vars.append(temp_vars)
        if vars == []:
            vars = [[]]
        
        return cpm_array(vars)


    def _pos_ys_var(self):

        w_repeats = self.nr_width_repeats()
        l_repeats = self.nr_length_repeats()
        vars = []

        self.min_move_y = np.zeros((self.length_repeats_upper()+1, self.nr_width_repeats()), dtype=int)
        self.max_move_y = np.zeros((self.length_repeats_upper()+1, self.nr_width_repeats()), dtype=int)

        for y in range(self.length_repeats_lower(),self.length_repeats_upper()+1):
            temp_vars = []
            for x in range(w_repeats): # TODO is voor elke x steeds hetzelfde, kan berekening hergebruiken
                if y == 0 & y == l_repeats - 1: 
                    self.max_move_y[y,x] = self.bin_config.max_length - self.height   # TODO kan obv max packing zone
                elif y == 0:
                    self.max_move_y[y,x] = self.height - 1
                elif y == l_repeats - 1:
                    self.min_move_y[y,x] = y*self.height
                    self.max_move_y[y,x] = self.bin_config.max_length - self.height
                else:
                    self.min_move_y[y,x] = y*self.height
                    self.max_move_y[y,x] = (y+1)*self.height - 1

                temp_vars.append(intvar(self.min_move_y[y,x], self.max_move_y[y,x]))

            vars.append(temp_vars)
            
        if vars == []:
            vars = [[]]

        return cpm_array(vars)


    def _count_var(self):
        return intvar(0, self.nr_width_repeats()*self.nr_length_repeats())

    def _active_var(self):
        return boolvar((self.length_repeats_upper()-self.length_repeats_lower()+1, self.nr_width_repeats()))
    

    def __eq__(self, other):
        if isinstance(other, ItemPacking):
            return (self.item == other.item) & (self.count == other.count)
        else:
            return False
