
from src.data_structures.abstract_single_bin_packing import AbstractItemPacking
from .data_structures.creel_section import CreelSection
from src.models.single_bin.guillotine.model import GuillotineSBM

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

def within_color_section_guillotine(bin_model: GuillotineSBM, section: CreelSection):
    cc = []

    pattern_height = 0
    for p in range(bin_model.P): # go over patterns
        strip_width = 0
        for a in range(bin_model.A): # go over strips

            
            for i in range(bin_model.I): # go over items
                for color in bin_model.items[i].item.color.basic_colors:
                    if a == 0:
                        cc.append(
                            cpm_any(bin_model.sigma[p,a,:,i]).implies(
                                section.color_sections[section.colors.index(color)].is_here_2_fixed(strip_width, strip_width+bin_model.items[i].width)
                            )
                        )
                    else:
                        cc.append(
                            cpm_any(bin_model.sigma[p,a,:,i]).implies(
                                section.color_sections[section.colors.index(color)].is_here_2(strip_width, strip_width+bin_model.items[i].width)
                            )
                        )

            strip_width += sum(bin_model.gamma[p,a,:]*bin_model.widths) 

        pattern_height += bin_model.pattern_length[p]

    return cpm_all(cc)
      