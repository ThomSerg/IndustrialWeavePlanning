from __future__ import annotations

import numpy as np

from src.data_structures.textile_item import TextileItem
from src.data_structures.abstract_item_packing import AbstractItemPacking
from src.data_structures.machine_config import MachineConfig

from ...data_structures.creel_section import CreelSection
from ...data_structures.creel_config import CreelConfig
from ..creel_section_model import CreelSectionModel

from ...constraints import within_color_section


class CreelModel:

    # Constructor
    def __init__(self,
                    max_colors: int,
                    items: list[TextileItem],
                    single_bin_packing: AbstractItemPacking,
                    machine_config: MachineConfig,
                ):
        
        # Set attributes
        self.max_colors=max_colors
        self.items = items
        self.single_bin_packing = single_bin_packing
        self.machine_config = machine_config

        self.creel_delay_cost = machine_config.creel_switch_penalty # TODO hierarchische structuur van machine configs maken?

        # Collect all colors -> misschien meegeven bij constructor
        colors = []
        for item in self.items:
            colors.extend(item.item.color.basic_colors)
        colors = list(set(colors))

        self.colors = colors

    def get_constraints(self):
        c = []

        # Determine the minimal width of each color section based on all textile items with that color
        min_widths = [np.inf for i in range(len(self.colors))]
        for item in self.items:
            for basic_color in item.item.color.basic_colors:
                min_widths[self.colors.index(basic_color)] = min((min_widths[self.colors.index(basic_color)],item.width,item.height))

        creel_config = CreelConfig(
            total_width = self.machine_config.width, 
            max_colors=self.max_colors
        )

        creel_section = CreelSection(
            colors=self.colors,
            min_widths=min_widths,
            creel_config=creel_config
        )

        # Get constraints of creel sections
        creel_section_model = CreelSectionModel(creel_section, creel_config)
        c.extend(creel_section_model.get_constraints())


        c.append(within_color_section(self.single_bin_packing, creel_section))

        return c
    
    def get_objective(self):
        return 0
    
    def get_stats(self):
        return {}
    
    def print_stats(self):
        print(self.get_stats())

    