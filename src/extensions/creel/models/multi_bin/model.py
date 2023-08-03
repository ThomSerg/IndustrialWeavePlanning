from __future__ import annotations

import numpy as np

from cpmpy.expressions.python_builtins import all as cpm_all
from cpmpy.expressions.python_builtins import any as cpm_any
from cpmpy.expressions.python_builtins import sum as cpm_sum

from ...data_structures.creel_packing import CreelPacking
from ...models.creel_packing_model import CreelPackingModel

from src.data_structures.textile_item import TextileItem
from src.data_structures.abstract_item_packing import AbstractItemPacking
from src.extensions.due_dates.data_structures.bin_production import BinProduction
from src.data_structures.machine_config import MachineConfig
from src.models.single_bin_creel.abstract_single_bin_creel_model import AbstractSBMCreel


class CreelModel:

    # Constructor
    def __init__(self,
                    max_creel_number: int,
                    max_deadline: int,
                    max_colors: int,
                    items: list[TextileItem],
                    fixed_single_bin_packings: list[AbstractItemPacking],
                    single_bin_model: AbstractSBMCreel,
                    bin_production: list[BinProduction],
                    machine_config: MachineConfig,
                ):
        
        # Set attributes
        self.max_creel_number = max_creel_number
        self.max_deadline = max_deadline
        self.max_colors = max_colors
        self.items = items
        self.fixed_single_bin_packings = fixed_single_bin_packings
        self.single_bin_model = single_bin_model
        self.bin_production = bin_production
        self.machine_config = machine_config

        self.creel_delay_cost = machine_config.creel_switch_penalty

        # Collect all colors
        colors = []
        for item in self.items:
            colors.extend(item.color.basic_colors)
        colors = list(set(colors))

        self.colors = colors

    def get_constraints(self):
        c = []

        # Determine the minimal width of each color section based on all textile items with that color
        min_widths = [np.inf for _ in range(len(self.colors))]
        for item in self.items:
            for basic_color in item.color.basic_colors:
                min_widths[self.colors.index(basic_color)] = min((min_widths[self.colors.index(basic_color)],item.width,item.height))
            
        # Create all variables
        self.creel_packing = CreelPacking(
                max_creel_number=self.max_creel_number,
                max_deadline=self.max_deadline,
                max_colors=self.max_colors,
                colors=self.colors,
                min_widths=min_widths,
                machine_config=self.machine_config,
            )
        
        # Get constraints of creel packing
        self.creel_packing_model = CreelPackingModel(creel_packing=self.creel_packing)
        c.extend(self.creel_packing_model.get_constraints())


        # List with for each bin its color ranges
        bin_color_ranges = []
        for fsbp in self.fixed_single_bin_packings:
            color_ranges = {}

            for item in fsbp.items:
                    
                item_color_ranges = self.color_range_from_item(item)
                for basic_color in self.colors:
                    color_ranges[basic_color] = color_ranges.get(basic_color, []) + item_color_ranges.get(basic_color, [])

            for basic_color in self.colors:
                color_ranges[basic_color] = self.interval_union(color_ranges.get(basic_color, []))

            bin_color_ranges.append(color_ranges)



        # Link bin color range to creel section color range
        # - fixed bins
 
        # Iterate over all bins
        for i_deadline in range(len(self.bin_production.deadlines)):
            for i_bin,(bin_active,bin_start,bin_end) in enumerate(zip(self.bin_production.fixed_bin_active[:,i_deadline], self.bin_production.bin_starts[:,i_deadline], self.bin_production.bin_ends[:,i_deadline])):
 
                # Iterate over all creel sections
                for i_section,(section,section_start,section_end) in enumerate(zip(self.creel_packing.sections, self.creel_packing.starts, self.creel_packing.ends)):
                    
                    # Get all colors of the selected bin
                    colors = bin_color_ranges[i_bin].keys()

                    # The bin color range must be compatible with the section color range
                    cc = []
                    for color in colors: # Go over each color
                        for (x1,x2) in bin_color_ranges[i_bin][color]: # Look where that color is located inside the bin
                            cc.append(section.color_sections[section.colors.index(color)].is_here_2_fixed(x1,x2)) # Constraint the color section
                   
                    # Look for correct section where bin is located
                    c.append(
                        (bin_active).implies(   # Active bin
                            (i_section < self.creel_packing.count).implies( # Active creel section
                                ((section_start <= bin_start) & (bin_end <= section_end)).implies( # Bin lies within creel section
                                    cpm_all(cc)
                                )
                            )
                        )
                    )

                # If a bin is active, it must lie in a color section
                c.append(
                    (bin_active).implies(
                        cpm_any(
                            [
                                ((section_start <= bin_start) & (bin_end <= section_end) & (i_section < self.creel_packing.count)) 
                                for i_section,(section,section_start,section_end) in enumerate(zip(self.creel_packing.sections, self.creel_packing.starts, self.creel_packing.ends)) 
                            ]
                        )
                    )
                )
    
        # - free bins
        self.f = []
        self.cond = []
        for i_deadline in range(len(self.bin_production.deadlines)):
            for bin_packing,bin_active,bin_start,bin_end in zip(self.bin_production.fixable_bin_packings,self.bin_production.bin_active[-len(self.bin_production.fixable_bin_packings):,i_deadline], self.bin_production.bin_starts[-len(self.bin_production.fixable_bin_packings):,i_deadline],self.bin_production.bin_ends[-len(self.bin_production.fixable_bin_packings):,i_deadline]):
                for i_section,(section,section_start,section_end) in enumerate(zip(self.creel_packing.sections, self.creel_packing.starts, self.creel_packing.ends)):

                    # The bin color range must be compatible with the section color range
                    cc = self.single_bin_model.within_color_section(section)

                    # Look for correct section where bin is located
                    c.append(
                        (i_section < self.creel_packing.count).implies( # Active creel section
                            ((section_start <= bin_start) & (bin_end <= section_end)).implies( # Bin lies within creel section
                                cc
                            )
                        )
                    )
                    
                # If a bin is active, it must lie in a color section
                c.append(
                    (bin_active).implies(
                        cpm_any(
                            [
                                ((section_start <= bin_start) & (bin_end <= section_end) & (i_section < self.creel_packing.count)) for i_section,(section,section_start,section_end) in enumerate(zip(self.creel_packing.sections, self.creel_packing.starts, self.creel_packing.ends)) 
                            ]
                        )
                    )
                )

        self.bin_starts = self.bin_production.bin_starts
        self.bin_ends = self.bin_production.bin_ends

        # At least one creel section should be in use
        c.append(cpm_sum([ccs.count>0 for cs in self.creel_packing._creel_sections for ccs in cs.creel_color_sections]) > 1)

        return c

    def get_objectives(self):
        # Preference for earlier creel sections
        o1 = cpm_sum([start*(i < self.creel_packing.count) for (i,start) in enumerate(self.creel_packing.starts)])
        # Preference for earlier produced bins
        o2 = cpm_sum(np.multiply(self.bin_production.bin_starts, self.bin_production.bin_active))
        return o1 + o2

    def get_stats(self):
        return {}
    
    def print_stats(self):
        print("Creel Sections")
        print(self.creel_packing.count.value())
        start_stop = np.array([self.creel_packing.starts.value(), self.creel_packing.ends.value()]).T
        print(start_stop)
        print("Color Sections:")
        for i_creel_section, creel_section in enumerate(self.creel_packing.sections):
            print("- creel section", i_creel_section)
            for color_section in creel_section.color_sections:
                print(color_section.count.value(), color_section.color.tuple,  np.array([color_section.starts.value(), color_section.ends.value()]).T.flatten())


    def color_range_from_item(self, item):

        color = item.item.color
        color_ranges = {}

        for x in range(item.nr_width_repeats()):
            if any(item.active_arr[:,x]):
                for basic_color in color.basic_colors:
                    color_ranges[basic_color] = color_ranges.get(basic_color,[]) + [(min(item.pos_xs_arr[:,x]),max(item.pos_xs_arr[:,x])+item.width)]

        return color_ranges

    # code by eumiro (https://stackoverflow.com/questions/15273693/union-of-multiple-ranges)
    def interval_union(self, intervals):
        res = []
        for begin,end in sorted(intervals):
            if res and res[-1][1] >= begin - 1:
                res[-1][1] = max((res[-1][1], end))
            else:
                res.append([begin, end])
        return res