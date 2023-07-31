
from cpmpy.expressions.python_builtins import all as cpm_all
from cpmpy.expressions.python_builtins import any as cpm_any
from cpmpy.expressions.python_builtins import max as cpm_max
from cpmpy.expressions.python_builtins import min as cpm_min

from ...single_bin.anchor.model import AnchorSBM

from src.data_structures.machine_config import MachineConfig
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking
from src.extensions.creel.data_structures.creel_section import CreelSection
from src.models.single_bin_creel.abstract_single_bin_creel_model import AbstractSBMCreel


class AnchorSBMCreel(AnchorSBM, AbstractSBMCreel):

    '''
    CP-Anchor + creel model (for MLOPP)
    '''

    # Constructor
    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: AbstractSingleBinPacking,
                ):

        super().__init__(machine_config, single_bin_packing)
    
    def within_color_section(self, section: CreelSection):

        # The bin color range must be compatible with the section color range
        cc = []

        for item in self.single_bin_packing.items:
            for x in range(item.nr_width_repeats()):
                ccc = []
                for color in item.item.color.basic_colors:
                    ccc.append(
                        section.color_sections[section.colors.index(color)].is_here_2(cpm_min(item.pos_xs_arr[:,x]), cpm_max(item.pos_xs_arr[:,x])+item.width)
                    )
                cc.append(
                    (cpm_any(item.active_arr[:,x])).implies(
                        cpm_all(ccc)
                    )
                )

        return cpm_all(cc)

    def get_constraints(self):
        return super().get_constraints()
    

    def get_name():
        return "AnchorSBM&Creel"