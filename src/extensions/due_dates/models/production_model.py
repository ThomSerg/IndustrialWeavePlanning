
import itertools
import math
import numpy as np
import numpy.typing as npt
import time

from cpmpy import *
from cpmpy.solvers import CPM_ortools 
from cpmpy.expressions.python_builtins import all as cpm_all
from cpmpy.expressions.python_builtins import sum as cpm_sum
from cpmpy.expressions.python_builtins import any as cpm_any

from src.extensions.due_dates.data_structures.bin_production import BinProduction

from src.data_structures.machine_config import MachineConfig
from src.data_structures.production_schedule import ProductionSchedule
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking


from src.models.abstract_model import AbstractSingleBinModel, constraint

from src.data_structures.abstract_item_packing import AbstractItemPacking
from src.extensions.due_dates import objectives

#from iterative.creel.CreelModel import CreelModel


class ProductionModel():

    

    # Constructor
    def __init__(self,
                    machine_config: MachineConfig,
                    production_schedule: ProductionSchedule,
                    free_single_bins: list[AbstractSingleBinPacking],
                    items: list[AbstractItemPacking],
                    single_bin_model: AbstractSingleBinModel,
                ):
        
        # Set attributes
        self.machine_config = machine_config
        self.production_schedule = production_schedule
        self.free_single_bins = free_single_bins
        self.items = items
        self.single_bin_model = single_bin_model
        
        # All bin packings
        self.single_bin_packings = self.free_single_bins

        # Bin production
        self.bin_production = BinProduction(
            production_schedule=self.production_schedule, 
            fixed_bin_packings=[],
            fixable_bin_packings=self.free_single_bins
        )

        # Bin packing model
        self.single_bin_models = [
            self.single_bin_model(
                machine_config=self.machine_config, 
                single_bin_packing=free_single_bin,
                is_end_packing=True
            ) for free_single_bin in self.free_single_bins]

        # CPMpy 
        # -> model
        self.model = Model()
        # -> constraints
        self.constraints = []
        self.constraints_stats = {}
        # -> objective
        self.objective = 0

        # To collect data about the algorithm
        self.stats = {}

    @constraint
    def bin_active(self):
        c = []

        # If a bin is not active, it should not be repeated
        # If it is active, it should be repeated at least once
        for a,b in zip(self.bin_production.bin_active[-1,:],self.bin_production.bin_repeats[-1,:]):
            c.append(a == (b!=0))

        # TODO test performance
        # # If a bin is not active, it should not be repeated
        # c.append(cpm_all((~self.bin_production._bin_active).implies(self.bin_production.bin_repeats==0)))
        # # If a bin is active, it should be repeated at least once
        # c.append(cpm_all((self.bin_production._bin_active).implies(self.bin_production.bin_repeats!=0)))

        return c

    @constraint
    def bin_order(self):
        c = []

        # The order values must be unique per deadline
        for bin_order_per_deadline in self.bin_production.bin_order.T:
            c.append(AllDifferent(bin_order_per_deadline))

        # Active bins should come before inactive ones
        for ((bp_a_1, bp_a_2),(bp_o_1, bp_o_2)) in zip(itertools.permutations(self.bin_production.bin_active, 2), itertools.permutations(self.bin_production.bin_order, 2)):
            c.extend((bp_a_1 & ~bp_a_2).implies(bp_o_1 < bp_o_2)) # TODO combinations

        return c

    @constraint
    def deadline_capacity(self):
        c = []

        # There can only be as many bins in each deadline as there is time
        for i_deadline in range(len(self.bin_production.deadline_betweens)):
            c.append(sum(self.bin_production.bin_repeats[:,i_deadline]) <= self.bin_production.deadline_betweens[i_deadline])

        return c

    @constraint
    def unique_new_bin(self):
        c = []

        # The new bin solution must be unique
        for (sbp1, sbp2) in itertools.combinations(self.single_bin_packings, 2):
            c.append((sbp1 == sbp2).implies((cpm_sum(sbp1.counts) == 0) | (cpm_sum(sbp2.counts) == 0)))

        return c
    
    @constraint
    def symmetry_breaking(self):
        c = []

        for (sbp1, sbp2) in itertools.pairwise(self.single_bin_packings):
            c.append((sbp1.area) * sbp2.bin.area <= ((sbp2.area) * sbp1.bin.area))

        return c


    def get_constraints(self):
        c = []

        # Get constraints from the new bin packing model
        for sbm in self.single_bin_models:
            c.extend(sbm.get_constraints())

        c_functions = [
            self.bin_active,
            self.bin_order,
            self.deadline_capacity,
            self.unique_new_bin,
            self.symmetry_breaking
        ]

        for c_f in c_functions:
            c.extend(c_f())

        c.extend(self.constraints)
        self.constraints = c
    
        return c

    def get_objective(self):


        # onderproduction in elke deadline afstraffen, overproduction enkel op het einde
        # moet steeds werken met production untill!

        # Underproduction
        self.o1 = objectives.underproduction(self.production_schedule, self.bin_production)

        # Overproduction
        self.o2 = objectives.overproduction(self.production_schedule, self.bin_production)

        # Waste
        self.o3 = objectives.waste(self.bin_production, self.single_bin_packings)
   
        # Non-productive time
        # o4 = 0
        # o4 += sum(self.bin_production._bin_delays_after + self.bin_production._bin_delays_before)*400#*400 # TODO omzetten naar afstand ipv # bins

        # Lower left preference
        self.o5 = objectives.lower_left_preference(self.free_single_bins)

        # Very large number
        M = self.free_single_bins[0].bin.width*self.free_single_bins[0].bin.max_length
        M = self.free_single_bins[0].bin.max_length

        weight = [2*M, 1*M, 4*M, 0, 1] # No overproduction

        return weight[0]*self.o1 + weight[1]*self.o2 + weight[2]*self.o3 + weight[4]*self.o5 #+ weight[3]*o4


    def get_variables(self):
        var = []
        for fsb in self.free_single_bins:
            var += fsb.get_variables()
        var += self.bin_production.get_variables()
        return var


    def solve(self, max_time_in_seconds=1):

        self.c = self.get_constraints()
        self.stats["nr_constraints"] = len(self.c)
        print("nr_constraints", len(self.c))

        self.o = self.get_objective()
        self.objective += self.o

        print("objective:", self.o)

        self.model += self.constraints
        self.model.minimize(self.objective)

        print("Transferring...")
        start_t = time.perf_counter()
        s = CPM_ortools(self.model)
        end_t = time.perf_counter()
        self.stats["transfer_time"] = end_t - start_t

        print("Solving...")
        start_s = time.perf_counter()
        res = s.solve( max_time_in_seconds=max_time_in_seconds)
        end_s = time.perf_counter()
        self.stats["solve_time"] = end_s - start_s

        print("o1", self.o1.value())
        print("o2", self.o2.value())
        print("o3", self.o3.value())
        print("o5", self.o5.value())

        for fsb in self.free_single_bins:
            print(fsb.counts.value())
            print(fsb.area.value())
  

        # Fix the solution to bound variables
        if res:
            [fsb.fix() for fsb in self.free_single_bins]

        


        return res
    
    def get_stats(self):
        # TODO nieuwe statistieken voor multi bin packing algoritmen
        
        self.stats["objective"] = int(self.o.value())
        self.stats["nr_variables"] = len(self.get_variables())

        self.stats["nr_solutions"] = len(self.single_bin_packings)
        self.stats["deadlines"] = self.production_schedule.deadlines.astype(int).tolist()
        self.stats["deadline_betweens"] = self.bin_production.deadline_betweens.astype(int).tolist()
        self.stats["solution_repeats"] = np.array(self.bin_production.bin_repeats.value()).astype(int).tolist()
        # a = self.bin_production._item_counts[:-1,:].value()
        a = np.array([fsb.counts for fsb in self.free_single_bins])
        self.stats["bins"] = a.astype(int).tolist()
        self.stats["densities"] = [float(sol.density) for sol in self.single_bin_packings]
        self.stats["total_density"] = float(sum([sum(repeats)*sol.density for (repeats,sol) in zip(self.bin_production.bin_repeats.value(), self.single_bin_packings)]) / sum(self.bin_production.bin_repeats.value()))
        self.stats["bin_lengths"] = [int(sbp.bin.length) for sbp in self.single_bin_packings]
        self.stats["required"] = self.production_schedule.requirements.counts.astype(int).tolist()
        self.stats["fulfilled"] = self.bin_production.item_counts.value().astype(int).tolist()
        underproduction_filter = np.vectorize(lambda x: max((x,0)))
        a =  np.cumsum(self.production_schedule.get_requirements(), axis=1) - np.cumsum(self.bin_production.item_counts, axis=1)
        a = underproduction_filter(a)
        self.stats["underproduction"] = np.array(a.value()).astype(int).tolist()
        overproduction_filter = np.vectorize(lambda x: max((x,0)))
        b = np.cumsum(self.bin_production.item_counts, axis=1) - np.cumsum(self.production_schedule.get_requirements(), axis=1)
        b = overproduction_filter(b)
        self.stats["overproduction"] = np.array(b.value()).astype(int).tolist()

        return self.stats
    
    def visualise(self):
        for i_packing in range(len(self.single_bin_models)):
            self.single_bin_models[i_packing].visualise()


    def print_stats(self):
        # print("NR solutions:", len(self.single_bin_solutions))
        # print("Solution repeats:")
        # print(self.bin_production.bin_repeats.value())
        # print("Bins:")
        # a = self.bin_production._item_counts[:-1,:]
        # a = np.append(a, np.array([fsb.counts for fsb in self.free_single_bins]), axis=0)
        # print(a)
        # print("Densities:", [sol.density for sol in self.single_bin_solutions])
        # print([sol.area for sol in self.single_bin_solutions])
        # print([sol.overflow_area for sol in self.single_bin_solutions])
        # print("Total density:", sum([sum(repeats)*sol.density for (repeats,sol) in zip(self.bin_production.bin_repeats.value(), self.single_bin_solutions)]) / sum(self.bin_production.bin_repeats.value()))
        # print("Deadlines:")
        # print(self.production_schedule.deadlines)
        # print("Deadline betweens")
        # print(self.bin_production._deadline_betweens)
        # print("Required:")
        # print(self.production_schedule.requirements.counts)
        # print("Fulfilled:")
        # print(self.bin_production.item_counts.value())
        # print("Underproduction:")
        # underproduction_filter = np.vectorize(lambda x: max((x,0)))
        # a =  np.cumsum(self.production_schedule.get_requirements(), axis=1) - np.cumsum(self.bin_production.item_counts, axis=1)
        # a = underproduction_filter(a)
        # print(a.value())
        # print("Overproduction:")
        # overproduction_filter = np.vectorize(lambda x: max((x,0)))
        # b = np.cumsum(self.bin_production.item_counts, axis=1) - np.cumsum(self.production_schedule.get_requirements(), axis=1)
        # b = overproduction_filter(b)
        # print(b.value())

        self.single_bin_solutions = self.single_bin_packings

        print("NR solutions:", len(self.single_bin_solutions))
        print("Solution repeats:")
        print(self.bin_production.bin_repeats.value())
        print("Bins:")
        a = self.bin_production._item_counts
        print(a)
        print("Densities:", [sol.density for sol in self.single_bin_solutions])
        print("Total density:", sum([sum(repeats)*sol.density for (repeats,sol) in zip(self.bin_production.bin_repeats.value(), self.single_bin_solutions)]) / sum(self.bin_production.bin_repeats.value()))
        print("Deadlines:")
        print(self.production_schedule.deadlines)
        print("Deadline betweens")
        print(self.bin_production.deadline_betweens)
        print("Required:")
        print(self.production_schedule.requirements.counts)
        print("Fulfilled:")
        print(self.bin_production.item_counts.value())
        print("Underproduction:")
        underproduction_filter = np.vectorize(lambda x: max((x,0)))
        a =  np.cumsum(self.production_schedule.get_requirements(), axis=1) - np.cumsum(self.bin_production.item_counts, axis=1)
        a = underproduction_filter(a)
        print(a.value())
        print("Overproduction:")
        overproduction_filter = np.vectorize(lambda x: max((x,0)))
        b = np.cumsum(self.bin_production.item_counts, axis=1) - np.cumsum(self.production_schedule.get_requirements(), axis=1)
        b = overproduction_filter(b)
        print(b.value())




    


        


        