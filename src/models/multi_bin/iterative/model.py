from __future__ import annotations
from dataclasses import field

import math
import time

from src.data_structures.bin_config import BinConfig
from src.data_structures.machine_config import MachineConfig
from src.data_structures.production_schedule import ProductionSchedule
from src.data_structures.bin import Bin
from src.data_structures.item import Item
from src.models.abstract_model import AbstractProductionModel
from src.data_structures.problem.multi_bin_problem import MultiBinProblem
from src.models.abstract_model import AbstractSingleBinModel
from src.utils.configuration import Configuration


class IterativeMBM():

    '''
    CP-Iterative model
    '''

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
                          ) -> IterativeMBM:
        # Construct the model
        return cls(
            problem.get_machine_config(),
            problem.get_production_schedule(),
            production_model,
            single_bin_model
        )
    
    # Name of the model
    def get_name():
        return "MultiIterativeModel"
    
    # Solve the model
    def solve(self, config:Configuration, args: dict, bin_solutions=None):

        # Get benchmark settings
        nr_iterations = args.get("nr_iterations", 1)
        packing_timeout = args.get("packing_timeout", 60)
        production_timeout = args.get("production_timeout", 5)

        start_time = time.perf_counter()
        
        if bin_solutions is None: bin_solutions = [] # Collection of found patterns
        self.models = []        # To collect the models of every iteration
        sat = False             # Whether the total model is SAT

        # Perform the number of requested iterations
        for i_iteration in range(nr_iterations):

            print("--- CREATING NEW BIN ---")

            # Solve model to create one new bin in the context of the previously achieved production
            sat_, model = self.solve_one_bin(
                config=config,
                bin_solutions=bin_solutions.copy(), 
                max_time_in_seconds=packing_timeout
                )
        
            # Check the outcome
            if not sat_:
                print("NOT SAT")
                break
            print("SAT")

            # Get the bin packings
            bin_solutions.append(model.single_bin_packings[0])

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

        for model in self.models[0:2:-1]:
            model.single_bin_models[0].visualise()
        
        return sat, self.models
    
    def get_preference(self):
        return self.preference

    def update_preference(self, preference):
        self.preference = preference


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
        self.temp_model.print_stats()

        return sat, self.temp_model
    
    # Solve production planning with a new bin
    def solve_one_bin(self, 
                        config:Configuration,
                        bin_solutions=field(default_factory=lambda: []),    # The previous bin packings
                        max_time_in_seconds = 60*2                          # Limit solver time
                        ):

        start_time = time.perf_counter()

        # Items to pack and schedule
        temp_items = self.production_schedule.items

        # Bin config
        temp_bin_config = BinConfig(
            width = self.machine_config.width,
            min_length = self.machine_config.max_length-max([max((item.height, item.width)) for item in temp_items]),
            max_length = self.machine_config.max_length,
        )
        temp_items = self.filter_items(temp_items, temp_bin_config)

        # Item packings
        temp_item_packings = [
                self.single_bin_model.ItemPacking(
                        item = i, 
                        max_count = math.floor((self.machine_config.width*self.machine_config.max_length)/i.area),
                        bin_config = temp_bin_config
                    ) for i in temp_items]
        temp_item_packings_rotated = [
                self.single_bin_model.ItemPacking(
                        item = i, 
                        max_count = math.floor((self.machine_config.width*self.machine_config.max_length)/i.area),
                        bin_config = temp_bin_config,
                        rotation = True
                    ) for i in temp_items]

        # Free single bin
        free_single_bins = [
            self.single_bin_model.single_bin_packing(
                _items = temp_item_packings, 
                _items_rotated = temp_item_packings_rotated,
                bin = Bin(config=temp_bin_config),
            )]

        # Create model
        self.temp_model = self.production_model(
            machine_config = self.machine_config, 
            production_schedule = self.production_schedule, 
            fixed_single_bins = [],
            free_single_bins = free_single_bins, 
            items = temp_items,
            single_bin_model = self.single_bin_model,
        )

        # New unique solution
        self.temp_model.constraints.extend([free_single_bins[0] != bs for bs in bin_solutions])

        # Solve to get partial solution
        sat = self.temp_model.solve(config, max_time_in_seconds, self.get_preference())
        print("Packing SAT:", sat)

        # Get the new bin 
        free_single_bin_packing = self.temp_model.free_single_bins[0]
        if sat:
            free_single_bin_packing.fix()

            # Show the new bin
            self.temp_model.free_single_bin_models[0].visualise()

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
            stats[i] = model.get_stats()
        return stats
    
    def visualise(self):
        return self.temp_model.visualise()