from __future__ import annotations

import itertools
import numpy as np

from src.data_structures.machine_config import MachineConfig
from src.data_structures.problem.colored_single_bin_problem import ColoredSingleBinProblem
from src.data_structures.bin import Bin
from src.models.single_bin.baseline.item_packing import ItemPacking
from src.models.abstract_model import AbstractSingleBinModel, constraint
from src.models.constraints import non_overlap

from .Visualiser import show_bin_packing
from .single_bin_packing import SingleBinPacking

from cpmpy.expressions.python_builtins import sum as cpm_sum


class BaselineSBM(AbstractSingleBinModel):

    '''
    CP-Baseline model
    '''

    ItemPacking = ItemPacking               # item packing datatype
    single_bin_packing = SingleBinPacking   # bin packing datatype

    # Constructor
    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: SingleBinPacking
                ):
        super().__init__(machine_config, single_bin_packing)
    

    # Alternative constructor from problem formulation
    @classmethod
    def init_from_problem(cls, problem: ColoredSingleBinProblem) -> BaselineSBM:

        # Create the packing variables
        sbp = SingleBinPacking(
                _items=problem.get_item_packing(ItemPacking),
                bin=Bin(config=problem.get_bin_config()),
            )
        
        # Construct the model
        return cls(
            problem.get_machine_config(),
            sbp,
        )      
    
    # Name of the model
    def get_name():
        return "Baseline"


    # ---------------------------------------------------------------------------- #
    #                                  Constraits                                  #
    # ---------------------------------------------------------------------------- #

    @constraint
    def item_active(self):
        c = []

        for item in self.single_bin_packing.items:
            c.extend(item.active == (np.arange(item.max_count) < np.full_like(item.active, item.count)) )

        return c
    

    @constraint
    def within_bin(self):
        c = []

        for item in self.single_bin_packing.items:
            for i_instance in range(item.max_count):
                pxs = item.pos_xs[i_instance]
                pys = item.pos_ys[i_instance]
                # stay within the width
                c.append(pxs <= self.single_bin_packing.bin.width - item.widths[i_instance])
                # stay within the height
                c.append(pys + item.heights[i_instance] <= self.single_bin_packing.bin.length)
  
        return c
    
    @constraint
    def no_overlap(self):
        c = []

        # Two items of different type should not overlap
        for (item_1, item_2) in itertools.combinations(self.single_bin_packing.items, 2):
            for (i_instance_1, i_instance_2) in itertools.product(range(item_1.max_count), range(item_2.max_count)):
                
                c.append(
                    (
                        (item_1.active[i_instance_1]) & (item_2.active[i_instance_2])
                    ).implies(
                        non_overlap(item_1.pos_xs[i_instance_1], item_1.pos_ys[i_instance_1], item_1.widths[i_instance_1], item_1.heights[i_instance_1],
                                    item_2.pos_xs[i_instance_2], item_2.pos_ys[i_instance_2], item_2.widths[i_instance_2], item_2.heights[i_instance_2])
                    )

                )
        
        # Two items of the same type should not overlap
        for item in self.single_bin_packing.items:
            for (i_instance_1, i_instance_2) in itertools.combinations(range(item.max_count), 2): 

                c.append(
                    (
                        (item.active[i_instance_1]) & (item.active[i_instance_2])
                    ).implies(
                        non_overlap(item.pos_xs[i_instance_1], item.pos_ys[i_instance_1], item.widths[i_instance_1], item.heights[i_instance_1],
                                    item.pos_xs[i_instance_2], item.pos_ys[i_instance_2], item.widths[i_instance_2], item.heights[i_instance_2])
                    )
                )

        return c

        
    @constraint
    def anti_symmetry(self):
        c = []

        # Items of the same type have a predetermined spacial order
        for item in self.single_bin_packing.items:
            for (i_instance_1, i_instance_2) in itertools.pairwise(range(item.max_count)): 

                c.append(
                    (
                        (item.active[i_instance_1]) & (item.active[i_instance_2])
                    ).implies(
                        (item.pos_xs[i_instance_1] < item.pos_xs[i_instance_2]) |
                        (
                            (item.pos_xs[i_instance_1] == item.pos_xs[i_instance_2]) &
                            (item.pos_ys[i_instance_1] < item.pos_ys[i_instance_2]) 
                        )
                    )
                )
        
        return c


    def get_constraints(self):
        c = []

        c_functions = [
            self.item_active,
            self.item_count,
            self.item_selection,
            self.within_bin,
            self.no_overlap,
            self.anti_symmetry,
            self.bin_height,
        ]

        for c_f in c_functions:
            c.extend(c_f())

        c.extend(self.constraints)
        self.constraints = c

        return c

    def get_objective(self):

        # Waste
        o1 = (self.single_bin_packing.bin.area-self.single_bin_packing.area)

        # Preference for lower left corner
        o4 = cpm_sum([((item.pos_xs[i_instance] + item.pos_ys[i_instance])*(item.active[i_instance])) for item in self.single_bin_packing.items for i_instance in range(item.max_count)])

        # Very large number
        B = self.single_bin_packing.bin.width*self.single_bin_packing.bin.max_length

        # Multi-objective objective function
        o = o1*B + o4

        return o

    def get_variables(self):
        return self.single_bin_packing.get_variables()

    def fix(self):
        self.single_bin_packing.fix()
    
    def get_repeats(self):
        return sum([item.free_max_count for item in self.single_bin_packing.items])
    
    def get_stats(self):
        
        if self.sat:
            super().get_stats()
        else:
            self.stats.nr_variables = len(self.get_variables())

        return self.stats
    
    def visualise(self):
        return show_bin_packing(self.single_bin_packing)
            