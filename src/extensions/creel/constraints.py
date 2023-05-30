
from src.data_structures.abstract_single_bin_packing import AbstractItemPacking
from .data_structures.creel_section import CreelSection

from cpmpy.expressions.python_builtins import all as cpm_all
from cpmpy.expressions.python_builtins import any as cpm_any
from cpmpy.expressions.python_builtins import max as cpm_max
from cpmpy.expressions.python_builtins import min as cpm_min
from cpmpy.expressions.python_builtins import sum as cpm_sum
from cpmpy.expressions.variables import cpm_array

def within_color_section(bin_packing: AbstractItemPacking, section: CreelSection):


    # The bin color range must be compatible with the section color range
    cc = []
    for item in bin_packing.items:

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

      