from __future__ import annotations

import math
import time
import itertools

from dataclasses import dataclass, field


from src.data_structures.bin_config import BinConfig

from src.data_structures.machine_config import MachineConfig
from src.data_structures.production_schedule import ProductionSchedule
from src.data_structures.bin import Bin
from src.data_structures.item import Item

from src.models.abstract_model import AbstractProductionModel
from src.data_structures.problem.multi_bin_problem import MultiBinProblem

from src.models.abstract_model import AbstractSingleBinModel

from src.extensions.due_dates.models.production_model import ProductionModel


class BaselineMBM():

    # Constructor
    def __init__(self,
                    machine_config: MachineConfig,
                    production_schedule: ProductionSchedule,
                    production_model: AbstractProductionModel,
                    single_bin_model: AbstractSingleBinModel,
                ):
        
        # Set attributes of self
        self.machine_config = machine_config
        self.production_schedule = production_schedule
        self.production_model = production_model
        self.single_bin_model = single_bin_model
        
    # Alternative constructor from problem formulation
    @classmethod
    def init_from_problem(cls, 
                          problem: MultiBinProblem, 
                          production_model: AbstractProductionModel,
                          single_bin_model: AbstractSingleBinModel
                          ) -> BaselineMBM:
        # Construct the model
        return cls(
            problem.get_machine_config(),
            problem.get_production_schedule(),
            production_model,
            single_bin_model,
        )

    # Name of the model
    def get_name():
        return "MultiBaselineModel"

    def solve(self, args: dict):
        nr_packings = args.get("nr_packings", 1)
        timeout = args.get("timeout", 20)
        weights = args.get("weights", None)

        self.single_bin_packings = []

        items = self.production_schedule.items

        bin_config = BinConfig(
            width=self.machine_config.width,
            min_length=self.machine_config.max_length-max([max((item.height, item.width)) for item in items]), # TODO
            max_length=self.machine_config.max_length,
        )

        items = self.filter_items(items, bin_config) # TODO niet logisch pas, min length van bin zou hier afhankelijk van moeten zijn

               

        for i_packing in range(nr_packings):
            # Item packings
            item_packings = [
                    self.single_bin_model.ItemPacking(
                        item=i, 
                        max_count=math.floor((self.machine_config.width*self.machine_config.max_length)/i.area),
                        bin_config=bin_config
                    ) for i in items] # TODO: better bound
            item_packings_rotated = [
                    self.single_bin_model.ItemPacking(
                        item=i, 
                        max_count=math.floor((self.machine_config.width*self.machine_config.max_length)/i.area),
                        bin_config=bin_config,
                        rotation=True
                    ) for i in items] # TODO: better bound
            
            # Free single bin
            free_single_bin = \
                self.single_bin_model.single_bin_packing(
                    _items=item_packings, 
                    _items_rotated=item_packings_rotated,
                    bin=Bin(config=bin_config),
                )
            
            self.single_bin_packings.append(free_single_bin)

        

        self.production_model = ProductionModel(
            machine_config=self.machine_config, 
            production_schedule=self.production_schedule, 
            free_single_bins=self.single_bin_packings, 
            items=items,
            single_bin_model=self.single_bin_model,
        )

        

        sat = self.production_model.solve(timeout)
        print("Packing SAT:", sat)
        print("nr constraints:", len(self.production_model.constraints))

        self.production_model.print_stats()
        

        return sat

        


    # TODO code reuse
    def filter_items(self, items: list[Item], bin_config: BinConfig) -> list[Item]:
        items = [i for i in items if i.width <= bin_config.width]
        items = [i for i in items if i.height <= bin_config.max_length]
        items = [i for i in items if bin_config.get_max_bin_area() > i.area]
        return items
    

    def get_stats(self):
        return self.production_model.get_stats()
    
    def visualise(self):
        self.production_model.visualise()


            

