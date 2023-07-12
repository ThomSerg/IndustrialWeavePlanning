
import itertools
from dataclasses import dataclass

import math
import numpy as np
import numpy.typing as npt
from timeit import default_timer as timer
from typing import List, Optional

from cpmpy import *
from cpmpy.solvers import CPM_ortools 
from cpmpy.expressions.python_builtins import all as cpm_all
from cpmpy.expressions.python_builtins import sum as cpm_sum
from cpmpy.expressions.python_builtins import any as cpm_any

from src.extensions.due_dates.data_structures.bin_production import BinProduction

from src.data_structures.machine_config import MachineConfig
from src.data_structures.production_schedule import ProductionSchedule
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking


from src.models.abstract_model import AbstractSingleBinModel, constraint, Alarm, TimeoutException, AbstractStats

from src.data_structures.abstract_item_packing import AbstractItemPacking
from src.extensions.due_dates import objectives
from src.utils.configuration import Configuration

#from iterative.creel.CreelModel import CreelModel


class ProductionModel():

    

    # Constructor
    def __init__(self,
                    machine_config: MachineConfig,
                    production_schedule: ProductionSchedule,
                    fixed_single_bins: list[AbstractSingleBinPacking],
                    free_single_bins: list[AbstractSingleBinPacking],
                    items: list[AbstractItemPacking],
                    single_bin_model: AbstractSingleBinModel,
                ):
        
        # Set attributes
        self.machine_config = machine_config
        self.production_schedule = production_schedule
        self.fixed_single_bins = fixed_single_bins
        self.free_single_bins = free_single_bins
        self.items = items
        self.single_bin_model = single_bin_model
        
        # All bin packings
        self.single_bin_packings = self.fixed_single_bins + self.free_single_bins

        # Bin production
        self.bin_production = BinProduction(
            production_schedule=self.production_schedule, 
            fixed_bin_packings=self.fixed_single_bins,
            fixable_bin_packings=self.free_single_bins
        )

        # Bin packing model
        self.free_single_bin_models = [
            self.single_bin_model(
                machine_config=self.machine_config, 
                single_bin_packing=free_single_bin,
            ) for free_single_bin in self.free_single_bins]

        # CPMpy 
        # -> model
        self.model = Model()
        # -> constraints
        self.constraints = []
        self.constraints_stats = {}
        # -> objective
        self.objective = 0
        # -> preference weights
        M = self.machine_config.max_length*self.machine_config.width
        self.weights = [1*M, 1*M, 4*M, 0, 1]

        # To collect data about the algorithm
        self.stats = stats()

    @constraint
    def bin_active(self):
        c = []

        # If a bin is not active, it should not be repeated
        # If it is active, it should be repeated at least once
        # for a,b in zip(self.bin_production.bin_active[-1,:],self.bin_production.bin_repeats[-1,:]):
        #     c.append(a == (b!=0))

        # TODO test performance
        # # If a bin is not active, it should not be repeated
        c.append(cpm_all((~self.bin_production.bin_active).implies(self.bin_production.bin_repeats==0)))
        # # If a bin is active, it should be repeated at least once
        c.append(cpm_all((self.bin_production.bin_active).implies(self.bin_production.bin_repeats!=0)))

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
    def bin_starts(self):
        c = []

        # Get the start and end position of each bin section in terms of the total number of predecessing repeats
        between_deadline_repeats = np.insert(self.bin_production.deadline_betweens,0,0)
        deadlines_shifted = np.insert(self.bin_production.deadlines,0,-1)

        for i_deadline in range(len(self.bin_production.deadlines)):
            for i_bin in range(self.bin_production.nr_packings):

                c.append(
                    (self.bin_production.bin_order[i_bin,i_deadline] == 0).implies(
                        self.bin_production.bin_starts[i_bin,i_deadline] == deadlines_shifted[i_deadline] + self.bin_production.bin_delays_before[i_bin,i_deadline] + 1
                    )
                )
                c.append(
                    (self.bin_production.bin_order[i_bin,i_deadline] > 0).implies(
                        self.bin_production.bin_starts[i_bin,i_deadline] == cpm_sum( (self.bin_production.bin_ends[:,i_deadline] + self.bin_production.bin_delays_after[:,i_deadline])*(self.bin_production.bin_order[:,i_deadline] == self.bin_production.bin_order[i_bin,i_deadline]-1)) + self.bin_production.bin_delays_before[i_bin,i_deadline] + 1
                    )
                )

        return c
                    
    
    @constraint
    def bin_ends(self):
        c = []

        c.extend(
            self.bin_production.bin_ends == self.bin_production.bin_starts + self.bin_production.bin_repeats - 1
        )

        return c



    @constraint
    def deadline_capacity(self):
        c = []

        # There can only be as many bins in each deadline as there is time
        for i_deadline in range(len(self.bin_production.deadline_betweens)):
            c.extend(
                (
                    self.bin_production.bin_ends[:,i_deadline] +
                    self.bin_production.bin_delays_after[:,i_deadline]
                )*self.bin_production.bin_active[:,i_deadline] <= self.bin_production.deadlines[i_deadline])

        return c

    @constraint
    def unique_new_bin(self):
        c = []

        # The new bin solution must be unique
        for (sbp1, sbp2) in itertools.combinations(self.free_single_bins, 2):
            c.append((sbp1 == sbp2).implies((cpm_sum(sbp1.counts) == 0) | (cpm_sum(sbp2.counts) == 0)))

        return c
    
    @constraint
    def symmetry_breaking(self):
        c = []

        for (sbp1, sbp2) in itertools.pairwise(self.free_single_bins):
            c.append((sbp1.area) * sbp2.bin.area <= ((sbp2.area) * sbp1.bin.area))

        return c


    def get_constraints(self):
        c = []

        # Get constraints from the new bin packing model
        for sbm in self.free_single_bin_models:
            c.extend(sbm.get_constraints())

        c_functions = [
            self.bin_active,
            self.bin_order,
            self.bin_starts,
            self.bin_ends,
            self.deadline_capacity,
            self.unique_new_bin,
            self.symmetry_breaking
        ]

        for c_f in c_functions:
            c.extend(c_f())

        c.extend(self.constraints)
        self.constraints = c
    
        return c

    def get_objective(self, weights):


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
        if (len(self.free_single_bins) > 0):
            self.o5 = objectives.lower_left_preference(self.free_single_bins)
        else:
            self.o5 = 0

        return weights[0]*self.o1 + weights[1]*self.o2 + weights[2]*self.o3 + weights[4]*self.o5 #+ weight[3]*o4

    def get_weights(self):
        return self.weights
    
    def get_weights_filter(self, overproduction_objective=False):
        return [1, overproduction_objective, 1, 1, 1]

    def determine_weights(self, preference, overproduction_objective=False):
        if preference is None:
            return self.get_weights()
        return [p*w*f*len(self.get_weights()) for (p,w,f) in zip(preference, self.get_weights(), self.get_weights_filter(overproduction_objective))]


    def get_variables(self):
        var = []
        for fsb in self.free_single_bins:
            var += fsb.get_variables()
        var += self.bin_production.get_variables()
        return var


    def solve(self, config:Configuration, max_time_in_seconds=1, preference=None, overproduction_objective=False, constraint_creation_timeout=60*3, constraint_transfer_timeout=60*2):
        

        alarm = Alarm(config=config)
        
        self.sat = False

        try:
            print("Collecting constraints ...")

            alarm.start(constraint_creation_timeout) 
            self.c = self.get_constraints()
            self.stats.nr_constraints = len(self.c)
            print("nr_constraints", len(self.c))
            alarm.cancel()

            weights = self.determine_weights(preference, overproduction_objective)
            self.o = self.get_objective(weights)
            self.objective += self.o

            self.model += self.constraints
            self.model.minimize(self.objective)

            print("Transferring...")

            start_t = timer()
            alarm.start(constraint_transfer_timeout) 
            s = CPM_ortools(self.model)
            alarm.cancel()
            end_t = timer()
            self.stats.transfer_time = end_t - start_t

            print("Solving...")
            start_s = timer()
            res = s.solve( max_time_in_seconds=max_time_in_seconds)
            end_s = timer()
            self.stats.solve_time = end_s - start_s
 
        except TimeoutException as e: 
            print(e)
            return False
        
        # Fix the solution to bound variables
        if res:
            [fsb.fix() for fsb in self.free_single_bins]

        return res
        
    
    def get_stats(self):
        # TODO nieuwe statistieken voor multi bin packing algoritmen
        
        
        self.stats.nr_solutions = len(self.single_bin_packings)
        self.stats.deadlines = self.production_schedule.deadlines.astype(int).tolist()
        self.stats.deadline_betweens = self.bin_production.deadline_betweens.astype(int).tolist()
        
        self.stats.solution_repeats = np.array(self.bin_production.bin_repeats.value()).astype(int).tolist()
        self.stats.solution_starts = np.array(self.bin_production.bin_starts.value()).astype(int).tolist()
        self.stats.solution_ends = np.array(self.bin_production.bin_ends.value()).astype(int).tolist()
        self.stats.solution_active = np.array(self.bin_production.bin_active.value()).astype(bool).tolist()
        
        a = np.array([fsb.counts for fsb in self.free_single_bins])
        self.stats.bins = a.astype(int).tolist()
        self.stats.densities = [float(sol.density) for sol in self.single_bin_packings]
        self.stats.total_density = float(sum([sum(repeats)*sol.density for (repeats,sol) in zip(self.bin_production.bin_repeats.value(), self.single_bin_packings)]) / sum(self.bin_production.bin_repeats.value()))
        self.stats.bin_lengths = [int(sbp.bin.length) for sbp in self.single_bin_packings]
        self.stats.required = self.production_schedule.requirements.counts.astype(int).tolist()
        self.stats.fulfilled = self.bin_production.item_counts.value().astype(int).tolist()
        underproduction_filter = np.vectorize(lambda x: max((x,0)))
        a =  np.cumsum(self.production_schedule.get_requirements(), axis=1) - np.cumsum(self.bin_production.item_counts, axis=1)
        a = underproduction_filter(a)
        self.stats.underproduction = np.array(a.value()).astype(int).tolist()
        overproduction_filter = np.vectorize(lambda x: max((x,0)))
        b = np.cumsum(self.bin_production.item_counts, axis=1) - np.cumsum(self.production_schedule.get_requirements(), axis=1)
        b = overproduction_filter(b)
        self.stats.overproduction = np.array(b.value()).astype(int).tolist()

        return self.stats
    
    def visualise(self):
        for i_packing in range(len(self.free_single_bin_models)):
            self.free_single_bin_models[i_packing].visualise()


    def print_stats(self):


        self.single_bin_solutions = self.single_bin_packings

        print("NR solutions:", len(self.single_bin_solutions))
        print("Solution repeats:")
        print(self.bin_production.bin_repeats.value())
        print("Starts:")
        print(self.bin_production.bin_starts.value())
        print("Ends:")
        print(self.bin_production.bin_ends.value())
        print("Active:")
        print(self.bin_production.bin_active.value())
        print("Bins:")
        a = self.bin_production._item_counts
        #a[-1] = a[-1].value()
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


@dataclass
class stats(AbstractStats):

    nr_solutions : int = None
    deadlines : List[int] = None
    deadline_betweens : List[int] = None
    solution_repeats : List[List[int]] = None
    solution_starts : List[List[int]] = None
    solution_ends : List[List[int]] = None
    solution_active : List[List[bool]] = None

    bins : List[List[int]] = None
    densities : List[int] = None
    
    bin_lengths : List[int] = None
    required : List[List[int]] = None
    fulfilled : List[List[int]] = None
    underproduction : List[List[int]] = None
    overproduction : List[List[int]] = None



    


        


        