from __future__ import annotations

import math
import time
import itertools
import matplotlib.pyplot as plt

from dataclasses import dataclass, field
from cpmpy.expressions.python_builtins import sum as cpm_sum
from cpmpy.expressions.python_builtins import any as cpm_any


from src.data_structures.bin_config import BinConfig

from src.data_structures.machine_config import MachineConfig
from src.data_structures.production_schedule import ProductionSchedule
from src.data_structures.bin import Bin
from src.data_structures.item import Item

from src.models.abstract_model import AbstractProductionModel
from src.data_structures.problem.multi_bin_problem import MultiBinProblem

from src.models.abstract_model import AbstractSingleBinModel, constraint

from src.extensions.due_dates.models.production_model import ProductionModel

from src.utils.configuration import Configuration

class LnsMBM():

    # Constructor
    def __init__(self,
                    machine_config: MachineConfig,
                    production_schedule: ProductionSchedule,
                    production_model: AbstractProductionModel,
                    single_bin_model: AbstractSingleBinModel
                ):
        
        # Set attributes of self
        self.machine_config = machine_config
        self.production_schedule = production_schedule
        self.production_model = production_model
        self.single_bin_model = single_bin_model

        self.preference = [1/5]*5
        
    # Alternative constructor from problem formulation
    @classmethod
    def init_from_problem(cls, 
                          problem: MultiBinProblem, 
                          production_model: AbstractProductionModel,
                          single_bin_model: AbstractSingleBinModel
                          ) -> LnsMBM:
        # Construct the model
        return cls(
            problem.get_machine_config(),
            problem.get_production_schedule(),
            production_model,
            single_bin_model
        )
    
    # Name of the model
    def get_name():
        return "MultiLnsModel"
    
    # Solve the model
    def solve(self, config:Configuration, args: dict, bin_solutions=None):
        nr_iterations = args.get("nr_iterations", 1)
        packing_timeout = args.get("packing_timeout", 60)
        production_timeout = args.get("production_timeout", 5)

        start_time = time.perf_counter()
        
        if bin_solutions is None: bin_solutions = []
        # bin_solutions = []      # To collect the bin packings in between iterations
        self.models = []        # To collect the models of every iteration
        sat = False             # Whether the total model is SAT

        max_new_bin_repeat = -1             # Limit on how many times the newly created bin of an iteration may be repeated (-1 fro no limit)
        previous_bin_production = None      # The (fulfilled) bin production of the previous iteration

        # Perform the number of requested iterations
        for i_iteration in range(nr_iterations):

            print("--- CREATING NEW BIN ---")
            # Solve model to create one new bin in the context of the previously achieved production
            sat_, model = self.solve_one_bin(
                config=config,
                bin_solutions=bin_solutions.copy(), 
                max_new_bin_repeat=max_new_bin_repeat, 
                previous_bin_production=previous_bin_production,
                max_time_in_seconds=packing_timeout
                )
        
            # Check the outcome
            if not sat_:
                print("NOT SAT")
                break
            print("SAT")

            # Get the bin packings
            bin_solutions = model.single_bin_packings

            # Detect duplicate solution generation
            # duplicate_sol = False
            # for (bin_sol_1, bin_sol_2) in itertools.combinations(bin_solutions, 2):
            #     duplicate_sol |= (bin_sol_1 == bin_sol_2)
            # if duplicate_sol:
            #     break

            # Update datastructures
            self.models.append(model)
            sat = True

        # Re-solve model with current packings (no new bin) to get final planning
        print("--- LAST MODEL ---")
        # Solve production problem without new bin
        sat_, model = self.solve_packing(
            config=config,
            bin_solutions=bin_solutions.copy(), 
            overproduction=True,
            max_time_in_seconds=production_timeout
            )

        self.models.append(model)

        # Get statistics
        end_time = time.perf_counter()
        print("Computation time:", end_time - start_time, "seconds")

        for model in self.models[0:2:-1]: # TODO ?
            model.single_bin_models[0].visualise()
        
        return sat, self.models
    
    def get_preference(self):
        return self.preference

    def update_preference(self, preference):
        self.preference = preference
    
    # def solve_preference(self, args: dict, bin_solutions=field(default_factory=lambda: [])):
    #     # sat, models = self.solve(args)

    #     packing_timeout = args.get("packing_timeout", 60)
    #     production_timeout = args.get("production_timeout", 5)

    #     start_time = time.perf_counter()
        
    #     models = []
    #     #bin_solutions = [] #models[-1].single_bin_solutions  # To collect the bin packings in between iterations
    #     sat = False         # Whether the total model is SAT

    #     previous_bin_production = None      # The (fulfilled) bin production of the previous iteration

        
        
    #     print("--- FIXING PRODUCTION ---")
    #     sat_, model = self.solve_packing(bin_solutions=bin_solutions.copy())
    #     # Get the production for next iteration
    #     model.bin_production.fix()
    #     previous_bin_production = model.bin_production

    #     print("--- CREATING NEW BIN ---")
    #     # Solve model to create one new bin in the context of the previously achieved production
    #     sat_, model = self.solve_one_bin(
    #         bin_solutions=bin_solutions.copy(), 
    #         max_new_bin_repeat=-1, 
    #         previous_bin_production=previous_bin_production,
    #         max_time_in_seconds=packing_timeout
    #         )
    
    #     # Check the outcome
    #     if not sat_:
    #         print("NOT SAT")
    #         return sat, models
    #     print("SAT")

    #     # Get the bin packings
    #     bin_solutions = model.single_bin_solutions

    #     # Detect duplicate solution generation
    #     # duplicate_sol = False
    #     # for (bin_sol_1, bin_sol_2) in itertools.combinations(bin_solutions, 2):
    #     #     duplicate_sol |= (bin_sol_1 == bin_sol_2)
    #     # if duplicate_sol:
    #     #     return
    #     # -> niet meer mogelijk

        

    #     print("--- LAST MODEL ---")
    #     # Solve production problem without new bin
    #     sat_, model = self.solve_packing(
    #         bin_solutions=bin_solutions.copy(), 
    #         overproduction=True,
    #         max_time_in_seconds=production_timeout
    #         )
        
    #     # Update datastructures
    #     models.append(model)
    #     sat = True

            

    #     return sat, models



    # Solve production planning without new bin
    def solve_packing(self, 
                        config:Configuration,
                        bin_solutions=field(default_factory=lambda: []),    # The bin packings
                        overproduction=False,                               # Whether overproduction is allowed
                        max_time_in_seconds=5                               # Limit solver time
                      ):


        # The items for which to plan a production
        items = self.production_schedule.items
        
        # Create production model
        self.temp_model = self.production_model(
            machine_config=self.machine_config, 
            production_schedule=self.production_schedule, 
            fixed_single_bins=bin_solutions,
            free_single_bins=[],
            items=items,
            single_bin_model=self.single_bin_model
        )

    
        # Solve to get partial solution
        sat = self.temp_model.solve(config, max_time_in_seconds, self.get_preference(), overproduction_objective=True)
        print("Packing SAT:", sat)
        print("nr constraints:", len(self.temp_model.constraints))

        self.temp_model.print_stats()

        return sat, self.temp_model
    
    # Solve production planning with a new bin
    def solve_one_bin(self, 
                        config:Configuration,
                        bin_solutions=field(default_factory=lambda: []),    # The previous bin packings
                        previous_bin_production=None,                       # The previously achieved production 
                        max_new_bin_repeat=None,                            # Limit on how many times the newly created bin may be repeated
                        max_time_in_seconds = 60*2                          # Limit solver time
                        ):

        start_time = time.perf_counter()

        nr_new_bins = 1 # Support for finding multiple new bins at once

        # Items to pack and schedule
        temp_items = self.production_schedule.items

        # Bin config
        temp_bin_config = BinConfig(
            width=self.machine_config.width,
            min_length=self.machine_config.min_length,#-max([max((item.height, item.width)) for item in temp_items]), #temp_machine_config.min_length,
            max_length=self.machine_config.max_length,
        )
        temp_items = self.filter_items(temp_items, temp_bin_config) # TODO niet logisch pas, min length van bin zou hier afhankelijk van moeten zijn

        # Item packings
        temp_item_packings = [
                self.single_bin_model.ItemPacking(
                        item=i, 
                        max_count=math.floor((self.machine_config.width*self.machine_config.max_length)/i.area),
                        bin_config=temp_bin_config
                    ) for i in temp_items] # TODO: better bound
        temp_item_packings_rotated = [
                self.single_bin_model.ItemPacking(
                        item=i, 
                        max_count=math.floor((self.machine_config.width*self.machine_config.max_length)/i.area),
                        bin_config=temp_bin_config,
                        rotation=True
                    ) for i in temp_items] # TODO: better bound

        # Free single bin
        free_single_bins = [
            self.single_bin_model.single_bin_packing(
                _items=temp_item_packings, 
                _items_rotated=temp_item_packings_rotated,
                bin=Bin(config=temp_bin_config),
            )]

        # Create model
        self.temp_model = self.production_model(
            machine_config=self.machine_config, 
            production_schedule=self.production_schedule, 
            fixed_single_bins=bin_solutions,
            free_single_bins=free_single_bins, 
            items=temp_items,
            single_bin_model=self.single_bin_model,
        )

        # Solve to get partial solution
        sat = self.temp_model.solve(config, max_time_in_seconds, self.get_preference())
        print("Packing SAT:", sat)
        print("nr constraints:", len(self.temp_model.constraints))

        # Get the new bin 
        free_single_bin_packing = self.temp_model.free_single_bins[0]
        if sat:
            self.temp_model.free_single_bin_models[0].fix()

            # Show the new bin
            self.temp_model.free_single_bin_models[0].visualise()
            plt.show()

            print("STATS:", self.temp_model.get_stats())
            self.temp_model.print_stats()

        
        # Get statistics
        end_time = time.perf_counter()
        print("Computation time:", end_time - start_time, "seconds")
       
        return sat, self.temp_model

    def filter_items(self, items: list[Item], bin_config: BinConfig) -> list[Item]:
        items = [i for i in items if i.width <= bin_config.width]
        items = [i for i in items if i.height <= bin_config.max_length]
        items = [i for i in items if bin_config.get_max_bin_area() > i.area]
        return items
    
    def get_stats(self):
        stats = {}
        for i, model in enumerate(self.models):
            stats[i] = model.get_stats().to_dict()
        return stats
    
    def visualise(self):
        return self.temp_model.visualise()
    
class ProductionModelLNS(ProductionModel):

    @constraint
    def unique_new_bin(self):
        c = []

        # The new bin solution must be unique
        c.extend(super().unique_new_bin())

        for sbpfree in self.free_single_bins:
            for sbpfixed in self.fixed_single_bins:
                c.append(~(sbpfree == sbpfixed))

        return c

    @constraint
    def usefull_bin(self):
        # The newly created bins should be used at least once to avoid creating garbage
        if len(self.free_single_bins) != 0:
            return [cpm_any(self.bin_production.fixable_bin_active.flatten().tolist())] 
        else: return []
    

    def get_constraints(self):
        c = []
        c = super().get_constraints()
        c.extend(self.usefull_bin())
        c.extend(self.unique_new_bin())
        c.append(cpm_any(self.bin_production.bin_active.flatten().tolist()))
        self.constraints = c
        return c
