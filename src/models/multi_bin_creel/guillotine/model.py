from __future__ import annotations

import math

from cpmpy.expressions.python_builtins import all as cpm_all
from cpmpy.expressions.python_builtins import any as cpm_any
from cpmpy.expressions.python_builtins import sum as cpm_sum

from ...single_bin.guillotine.model import GuillotineSBM
from ...single_bin.anchor.single_bin_packing import SingleBinPacking

from src.data_structures.machine_config import MachineConfig
from src.extensions.creel.data_structures.creel_section import CreelSection
from src.models.single_bin_creel.abstract_single_bin_creel_model import AbstractSBMCreel


class GuillotineSBMCreel(GuillotineSBM, AbstractSBMCreel):

    '''
    CP-Guillotine + creel model (for MLOPP)
    '''

    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: SingleBinPacking,
                ):
        
        super().__init__(machine_config, single_bin_packing)

    def within_color_section(self, section: CreelSection):
        cc = []

        for p in range(self.P): # go over patterns
            strip_width = 0
            for a in range(self.A): # go over strips

                for i in range(self.I): # go over items
                    item = self.single_bin_packing.items[i]
                    for color in item.item.color.basic_colors:
                        if a == 0:
                            cc.append(
                                cpm_any(self.sigma[p,a,:,i]).implies(
                                    section.color_sections[section.colors.index(color)].is_here_2_fixed(strip_width, strip_width+item.width)
                                )
                            )
                        else:
                            cc.append(
                                cpm_any(self.sigma[p,a,:,i]).implies(
                                    section.color_sections[section.colors.index(color)].is_here_2(strip_width, strip_width+item.width)
                                )
                            )

                strip_width += cpm_sum(self.gamma[p,a,:]*self.widths)
            
        return cpm_all(cc)

    def fix(self):
        super().fix()

        for i in range(self.I): # go over items

            item = self.single_bin_packing.items[i]
            item.fixable_active.fix()
            item.fixable_pos_xs_arr.fix()
            item.fixable_pos_ys_arr.fix()

            item.fixable_active.fixed=True
            item.fixable_pos_xs_arr.fixed=True
            item.fixable_pos_ys_arr.fixed=True

            item.fixable_active.fixed_value[:,:] = False

        pattern_height = 0
        for p in range(self.P): # go over patterns
            strip_width = 0
            for a in range(self.A): # go over strips
                cut_height = 0
                
                for b in range(self.B): # go over vertical cuts
                    for i in range(self.I): # go over items

                        if self.sigma[p,a,b,i].value():

                            item = self.single_bin_packing.items[i]
                            x_pos = strip_width
                            y_pos = (pattern_height+cut_height)

                            x_grid = min((math.floor(x_pos / item.width), item.nr_width_repeats()-1))
                            y_grid = min((math.floor(y_pos / item.height), item.nr_length_repeats()-1))

                            item.fixable_active.fixed_value[y_grid, x_grid] = self.sigma[p,a,b,i].value()
                            item.fixable_pos_xs_arr.fixed_value[y_grid, x_grid] = x_pos
                            item.fixable_pos_ys_arr.fixed_value[y_grid, x_grid] = y_pos

                            self.single_bin_packing.items[i] = item
                        
                            cut_height += self.items[i].height
                            break

                strip_width += sum(self.gamma[p,a,:].value()*self.widths) 

            pattern_height += self.pattern_length[p].value()

    def get_constraints(self):
        return super().get_constraints()
    
    def get_name():
        return "Guillotine&Creel"