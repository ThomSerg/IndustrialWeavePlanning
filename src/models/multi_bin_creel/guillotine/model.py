from __future__ import annotations

from ...single_bin.guillotine.model import GuillotineSBM

from src.models.abstract_model import AbstractSingleBinModel, constraint
from src.data_structures.bin import Bin
from src.data_structures.machine_config import MachineConfig
from ...single_bin.anchor.single_bin_packing import SingleBinPacking

from src.extensions.creel.models.single_bin.model import CreelModel
from src.extensions.creel.data_structures.creel_section import CreelSection
from src.models.single_bin_creel.abstract_single_bin_creel_model import AbstractSBMCreel

from cpmpy.expressions.python_builtins import all as cpm_all
from cpmpy.expressions.python_builtins import any as cpm_any
from cpmpy.expressions.python_builtins import sum as cpm_sum


class GuillotineSBMCreel(GuillotineSBM, AbstractSBMCreel):

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

    def get_constraints(self):
        return super().get_constraints()
    
    def get_name():
        return "Guillotine&Creel"