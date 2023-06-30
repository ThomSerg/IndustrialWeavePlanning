from __future__ import annotations
import itertools

import math
import time
from timeit import default_timer as timer

import numpy as np
from src.data_structures.bin import Bin

from src.data_structures.machine_config import MachineConfig
from .single_bin_packing import SingleBinPacking

import functools, operator


from cpmpy import Model, AllEqual
from cpmpy.solvers import CPM_ortools 
from cpmpy.expressions.python_builtins import all, any
from cpmpy.expressions.python_builtins import sum as cpm_sum
from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname
from cpmpy.expressions.globalconstraints import Element, Xor

from src.models.abstract_model import AbstractSingleBinModel, constraint
from src.data_structures.problem.problem import Problem

from src.models import objectives

from .Visualiser import show_bin_packing
from .item_packing import ItemPacking


class AnchorSBM(AbstractSingleBinModel):

    ItemPacking = ItemPacking
    single_bin_packing = SingleBinPacking
    
    # Constructor
    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: SingleBinPacking
                ):

        super().__init__(machine_config, single_bin_packing)

    # Alternative constructor from problem formulation
    @classmethod
    def init_from_problem(cls, problem) -> AnchorSBM:
        # Create packing variables
        sbp = SingleBinPacking(
                _items=problem.get_item_packing(ItemPacking),
                _items_rotated=problem.get_item_packing_rotated(ItemPacking),
                bin=Bin(config=problem.get_bin_config()),
            )

        # Construct the model
        return cls(
            problem.get_machine_config(),
            sbp,
        )
    
    # Name of the model
    def get_name():
        return "Anchor"

    # ---------------------------------------------------------------------------- #
    #                                  Constraits                                  #
    # ---------------------------------------------------------------------------- #



    
    
    @constraint
    def unselected_items(self):
        c = []

        # Link the position of every unselected item to that of the next (unselected) item
        # -> gives some determinism to all items, regardless whether they are selected
        # -> allows for reasoning over item position without having to check whether a specific instance is active

        # Go over all items
        for item in self.single_bin_packing.items:
            # Go over all instances of an item
            y_lower = item.length_repeats_lower()
            y_upper = item.length_repeats_upper()
            for y in range(y_lower, y_upper+1):
                for x in range(item.nr_width_repeats()):
                    
                    # Fix the x-position of an inactive instance to the x-position of the next instance
                    if y != y_upper:
                        c.append((item.active_arr[y,x] == 0).implies(
                            (item.pos_xs_arr[y,x] == item.pos_xs_arr[y+1,x])
                            ))
                    # When there is no next, fix to the first (creates possible loop)
                    else:
                        c.append((item.active_arr[y,x] == 0).implies(
                            (item.pos_xs_arr[y,x] == item.pos_xs_arr[y_lower,x])
                            ))
    
        return c
    
    @constraint
    def within_bin(self):
        c = []

        for item in self.single_bin_packing.items:
            l = max(((self.single_bin_packing.bin.min_length // item.height - 1), 0))
            #u = max(((self.single_bin_packing.bin.max_length // item.height - 1), 0))
            for y in range(l,item.nr_length_repeats()):
                for x in range(item.nr_width_repeats()):
                    c.append(
                        item.active_arr[y,x].implies(
                            item.pos_ys_arr[y,x] + item.heights_arr[y,x] <= self.single_bin_packing.bin.length
                        )
                    )
        #     #c.extend((item.pos_ys_arr[l:,:] + item.heights_arr[l:,:])*item.active_arr[l:,:] <= self.single_bin_packing.bin.length)
        
        return c

    @constraint
    def no_overlap(self):
        c = []

        # Don't allow item instances to overlap

        # Two items of different type should not overlap
        for (item_1, item_2) in itertools.combinations(self.single_bin_packing.items, 2):
   
            # Get item packing index ranges
            min_y_1, max_y_1 = item_1.length_repeats_lower(), item_1.length_repeats_upper()
            min_y_2, max_y_2 = item_2.length_repeats_lower(), item_2.length_repeats_upper()
            max_x_1, max_x_2 = item_1.nr_width_repeats(), item_2.nr_width_repeats()

            # Get position variables
            pos_xs_1, pos_xs_2 = item_1.pos_xs_arr, item_2.pos_xs_arr
            pos_ys_1, pos_ys_2 = item_1.pos_ys_arr, item_2.pos_ys_arr

            # Get item shapes
            w_1, w_2 = item_1.width, item_2.width
            h_1, h_2 = item_1.height, item_2.height

            y_1_lower = 0

            for y_1 in range(y_1_lower, max_y_1+1):
                
                for x_1 in range(0, max_x_1):

                    # y2*h2 + 2*h2-1 > y1*h1
                    y_2_lower = max((math.ceil((y_1*h_1 - 2*h_2 + 1)/h_2), 0))

                    # y1*h1 + 2*h1-1 > y2*h2 
                    y_2_upper = min((math.floor(((y_1+2)*h_1 - 1)/h_2), max_y_2))

                    x_2_lower = max((math.ceil((x_1*w_1 - 2*w_2 + 1)/w_2), 0))
                    x_2_upper = min((math.floor(((x_1+2)*w_1 - 1)/w_2), max_x_2-1))

                    for y_2 in range(y_2_lower, y_2_upper+1):
                        for x_2 in range(x_2_lower, x_2_upper+1):

                            pos_x_1 = pos_xs_1[y_1,x_1]
                            pos_x_2 = pos_xs_2[y_2,x_2]
                            pos_y_1 = pos_ys_1[y_1,x_1]
                            pos_y_2 = pos_ys_2[y_2,x_2]
                                                        
                            # TODO test met nieuwe formulering
                            a_1 = item_2.max_move_x[y_2,x_2]
                            c_1 = ((x_2+1)*w_2) - (x_2*w_2 - item_2.min_move_x[y_2,x_2])
                            b_1 = item_2.max_move_y[y_2,x_2]
                            d_1 = ((y_2+1)*h_2) - (y_2*h_2 - item_2.min_move_y[y_2,x_2])

                            a_2 = item_1.max_move_x[y_1,x_1]
                            c_2 = ((x_1+1)*w_1) - (x_1*w_1 - item_1.min_move_x[y_1,x_1])
                            b_2 = item_1.max_move_y[y_1,x_1]
                            d_2 = ((y_1+1)*h_1) - (y_1*h_1 - item_1.min_move_y[y_1,x_1])

                            # items die zeker overlappen, haalde niet veel uit, zelfde aantal constraints, klein beetje sneller (0.5s), ook iets sneller transfer time
                            # -> komt neer op dat één item in een ander ligt
                            if (min(d_1,d_2) > max(b_1,b_2)) and (min(c_1,c_2) > max(a_1,a_2)):

                                if y_2 < min_y_2 and item_2.active_arr[y_2,x_2]:
                                    c.append(~item_1.active_arr[y_1,x_1])
                                elif y_1 < min_y_1 and item_1.active_arr[y_1,x_1]:
                                    c.append(~item_2.active_arr[y_2,x_2])
                                else:
                                    c.append(~all([item_1.active_arr[y_1,x_1],item_2.active_arr[y_2,x_2]]))
                                continue

                            consequence = []
                            
                            if y_1*h_1 <= y_2*h_2:
                            #if c_y_1 <= c_y_2:
                                consequence.append( (pos_y_1 + h_1 <= pos_y_2) )
                            if y_2*h_2 <= y_1*h_1:
                            #if c_y_2 <= c_y_1:
                                consequence.append( (pos_y_2 + h_2 <= pos_y_1) )
                            if x_1*w_1 <= x_2*w_2:
                            #if c_x_1 <= c_x_2:
                                consequence.append( (pos_x_1 + w_1 <= pos_x_2) )
                            if x_2*w_2 <= x_1*w_1:
                            #if c_x_2 <= c_x_1:
                                consequence.append( (pos_x_2 + w_2 <= pos_x_1) )

                            c.append(
                                (item_1.active_arr[y_1,x_1] & item_2.active_arr[y_2,x_2]).implies(
                                    any(consequence)
                                )
                            )

    
        # Two items of the same type should not overlap
        for item in self.single_bin_packing.items:

            # Get position variables
            pos_xs = item.pos_xs_arr
            pos_ys = item.pos_ys_arr

            # Get item shape
            w = item.width
            h = item.height

            # Get item packing index ranges
            x_size = item.nr_width_repeats()
            min_y = item.length_repeats_lower()
            max_y = item.length_repeats_upper()

            for y in range(min_y,max_y+1):
                for x in range(x_size):

                    # No X overlap
                    if x != x_size-1: 
                        c.append(
                                (item.active[x+y*x_size] & item.active[x+1+y*x_size]).implies(
                                    pos_xs[y,x] + w <= pos_xs[y,x+1])
                            )

                    # No Y overlap
                    if y != max_y: 
                        c.append(
                                (item.active_arr[y,x] & item.active_arr[y+1,x]).implies(
                                    pos_ys[y,x] + h <= pos_ys[y+1,x])
                            )

                    # No X and Y overlap
                    if y != max_y: 
                        if x != 0:
                            c.append(
                                (item.active[x+y*x_size] & item.active[(x-1)+(y+1)*x_size]).implies(
                                    (pos_xs[y+1,x-1] + w <= pos_xs[y,x]) |
                                    (pos_ys[y,x] + h <= pos_ys[y+1,x-1]))
                            )
                        if x != x_size-1: 
                            c.append(
                                (item.active[x+y*x_size] & item.active[(x+1)+(y+1)*x_size]).implies(
                                    (pos_xs[y,x] + w <= pos_xs[y+1,x+1]) |
                                    (pos_ys[y,x] + h <= pos_ys[y+1,x+1]))
                            )

        print("nr_no_overlap", len(c))

        return c
    
    @constraint
    def bin_capacity(self):
        c = []

        # The total sum of the packed items' areas should not exceed the total bin area
        #c.append(sum([sum(item.active)*item.item.area for item in self.single_bin_packing.items]) <= self.single_bin_packing.bin.area)

        return c


    def get_constraints(self):
        c = []

        start = timer()

        c_functions = [
            self.item_count,
            self.item_selection,
            self.no_overlap,
            self.bin_height,
            self.bin_capacity
        ]

        if self.machine_config.min_length != self.machine_config.max_length:
            c_functions.append(
                self.within_bin
            )

        for c_f in c_functions:
            c.extend(c_f())

        c.append(self.single_bin_packing.bin.length < self.single_bin_packing.bin.max_length)

        self.constraints = c

        end = timer()
        self.stats["constraint_time"] = end-start
        
        return c

    def get_objective(self):

        # Waste
        o1 = objectives.waste(self.single_bin_packing)

        # Preference for lower left corner
        o4 = cpm_sum([((item.pos_xs[i_instance] + item.pos_ys[i_instance])*(item.active[i_instance])) for item in self.single_bin_packing.items for i_instance in range(item.nr_length_repeats()*item.nr_width_repeats())])

        # Very large number
        M = self.single_bin_packing.bin.width*self.single_bin_packing.bin.max_length

        # Multi-objective objective function
        o = M*o1 + o4

        return o

    def get_variables(self):
        return self.single_bin_packing.get_variables()
    
    def fix(self):
        self.single_bin_packing.fix()
    
    def get_repeats(self):
        return sum([item.nr_width_repeats()*item.nr_length_repeats() for item in self.single_bin_packing.items])

    def get_stats(self):

        self.stats["density"] = float(self.single_bin_packing.density)
        self.stats["bin_length"] = int(self.single_bin_packing.bin.length)
        self.stats["fulfilled"] = np.array(self.single_bin_packing.counts).astype(int).tolist()
        self.stats["counts"] = np.array(self.single_bin_packing.counts).astype(int).tolist()
        self.stats["repeats_width"] = [item.nr_width_repeats() for item in self.single_bin_packing.items]
        self.stats["repeats_length"] = [item.nr_length_repeats() for item in self.single_bin_packing.items]
        self.stats["objective"] = int(self.o.value())
        self.stats["nr_variables"] = len(self.get_variables())
        #self.stats["ortools_nr_constraints"] = len(self.model.constraints)
        self.stats["ortools_objective"] = int(self.model.objective_value())

        self.stats["constraints"] = self.constraints_stats

        return self.stats

    def visualise(self):
        return show_bin_packing(self.single_bin_packing)

            