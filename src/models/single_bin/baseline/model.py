from __future__ import annotations
import itertools

import numpy as np
import math
import time
import signal

from src.data_structures.machine_config import MachineConfig
from .single_bin_packing import SingleBinPacking
from src.data_structures.problem.colored_single_bin_problem import ColoredSingleBinProblem
from src.data_structures.bin import Bin
from src.models.single_bin.baseline.item_packing import ItemPacking
from .Visualiser import show_bin_packing
from src.models.abstract_model import AbstractSingleBinModel, constraint

from cpmpy import Model
from cpmpy.solvers import CPM_ortools 
from cpmpy.expressions.python_builtins import all, any
from cpmpy.expressions.python_builtins import sum as cpm_sum

from src.models.constraints import non_overlap

# def handler(signum, frame):
#     print("Forever is over!")
#     raise Exception("end of time")

# try:
#     signal.signal(signal.SIGALRM, handler)
# except:
#     pass
   

class BaselineSBM(AbstractSingleBinModel):
    
    # Constructor
    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: SingleBinPacking
                ):

        # Save the provided arguments as attributes
        self.machine_config = machine_config
        self.single_bin_packing = single_bin_packing

        # CPMpy model data
        self.constraints = []
        self.objective = 0
        self.model = Model()

        # To collect data about the algorithm
        self.stats = {}


    # Alternative constructor from problem formulation
    @classmethod
    def init_from_problem(cls, problem: ColoredSingleBinProblem) -> Model:
        # Create items to pack
        items = [
            ItemPacking(
                    item=i, 
                    max_count=math.floor((problem.machine_width*problem.machine_max_length)/i.area), 
                    bin_config=problem.get_bin_config(),
                ) for i in problem.get_items()
        ]
        # Create the packing variables
        sbp = SingleBinPacking(
                _items=items,
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
    def item_count(self):
        c = []

        for item in self.single_bin_packing.items:
            c.append(item.count == cpm_sum(item.active))

        return c

    @constraint
    def item_selection(self):
        c = []

        # If an item is active, it should be packed at least once
        # If an item is inactive, it should not be packed
        for item in self.single_bin_packing.items:

            c.extend([
                (~item.selected).implies(item.count == 0),
                (item.selected).implies(item.count != 0)
            ])

        return c

    @constraint
    def within_bin(self):
        c = []

        for item in self.single_bin_packing.items:
            for i_instance in range(item.max_count):
                pxs = item.pos_xs[i_instance]
                pys = item.pos_ys[i_instance]
                # Stay within the width
                c.append(pxs <= self.single_bin_packing.bin.width - item.widths[i_instance])
                # stay within the height
                c.append(pys + item.heights[i_instance] <= item.bin_config.max_packing_zone)
  
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


    @constraint
    def bin_height(self):
        c = []

        # The bin length should be at least its minimal value
        c.append(
            self.single_bin_packing.bin.length >= self.single_bin_packing.bin.config.min_length
        )

        for item in self.single_bin_packing.items:
            for i_instance in range(item.max_count):
                c.append(
                    (
                        item.active[i_instance]
                    ).implies(
                        item.pos_ys[i_instance] <= self.single_bin_packing.bin.length - item.heights[i_instance]
                    )
                )

        return c
    
    def get_constraints_per_type(self):
        return {
            "item_active": self.item_active(),
            "item_count": self.item_count(),
            "item_selection" : self.item_selection(),
            "within_bin": self.within_bin(),
            "no_overlap": self.no_overlap(),
            "anti_symmetry": self.anti_symmetry(),
            "bin_height": self.bin_height(),
        }

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

        print(c)
        
        return c

    def get_objective(self):

        # Waste
        o1 = (self.single_bin_packing.bin.area-self.single_bin_packing.area)

        # Preference for lower left corner
        o4 = cpm_sum([((item.pos_xs[i_instance] + item.pos_ys[i_instance])*(item.active[i_instance])) for item in self.single_bin_packing.items for i_instance in range(item.max_count)])

        # Very large number
        M = self.single_bin_packing.bin.width*self.single_bin_packing.bin.max_length

        # Multi-objective objective function
        o = o1*M + o4

        return o

    def get_variables(self):
        return self.single_bin_packing.get_variables()


    def solve(self, max_time_in_seconds=1):

        self.c = self.get_constraints()
        print("constraints", self.c)
        self.stats["nr_constraints"] = len(self.c)

        self.o = self.get_objective()
        self.objective += self.o

        self.model += self.constraints
        self.model.minimize(self.objective)
        
        self.sat = False

        print("Transferring...")
        #try:
        start_t = time.perf_counter()
        #signal.alarm(60) 
        s = CPM_ortools(self.model)
        #signal.alarm(0)
        end_t = time.perf_counter()
        self.stats["transfer_time"] = end_t - start_t

        print("Solving...")
        start_s = time.perf_counter()
        res = s.solve( max_time_in_seconds=max_time_in_seconds)
        end_s = time.perf_counter()
        self.stats["solve_time"] = end_s - start_s
        # except: 
        #     return False

        # Fix the solution to bound variables
        if res:
            self.sat = True
            self.single_bin_packing.fix()

        return res
    
    def fix(self):
        self.single_bin_packing.fix()
    
    def get_repeats(self):
        return sum([item.free_max_count for item in self.single_bin_packing.items])
    
    def get_stats(self):
        if self.sat:
            self.stats["density"] = float(self.single_bin_packing.density)
            self.stats["bin_length"] = int(self.single_bin_packing.bin.length)
            self.stats["fulfilled"] = np.array(self.single_bin_packing.counts).astype(int).tolist()
            self.stats["counts"] = np.array(self.single_bin_packing.counts).astype(int).tolist()
            self.stats["objective"] = int(self.o.value())
            self.stats["nr_variables"] = len(self.get_variables())
            #self.stats["ortools_nr_constraints"] = len(self.model.constraints)
            self.stats["ortools_objective"] = int(self.model.objective_value())
        else:
            self.stats["nr_variables"] = len(self.get_variables())

        return self.stats
    
    def visualise(self):
        return show_bin_packing(self.single_bin_packing)
            