import numpy as np

from src.data_structures.production_schedule import ProductionSchedule
from src.extensions.due_dates.data_structures.bin_production import BinProduction
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking

from cpmpy import max as cpm_max
from cpmpy import sum as cpm_sum

def underproduction(
            production_schedule : ProductionSchedule,   # The request
            bin_production : BinProduction,             # The fulfillment
        ):
    
    # demand[i] - ( sum(produced[:i]) - sum(demand[:i-1]) )
    # = sum(demand[:i]) - sum(produces[:i])
    # -> remembers earlier demand not met, keeps punishing if not make up for it at later time

    # zou eerdere gemiste deadlines kunnen vergeten voor latere dealines om geen blijvend effect te hebben
    # -> dan veel max(..,0) operties

    # cumsum geeft natuurlijke bias om demands van eerdere deadlines zeker niet te missen

    # Filter only positive underproduction (otherwise overproduction)
    underproduction_filter = np.vectorize(lambda x: cpm_max((x,0)))

    # How much has not been fulfilled
    a = np.cumsum(production_schedule.get_requirements(), axis=1) - np.cumsum(bin_production.item_counts, axis=1)
    a = underproduction_filter(a)

    # Total underproduction for each item
    a = [sum(i) for i in a] # donkey

    # Punish underproduction based on item value (its surface area)
    o = sum( a[i_item]*item.area for (i_item,item) in enumerate(production_schedule.items) )

    return o

def overproduction(
        production_schedule : ProductionSchedule,   # The request
        bin_production : BinProduction,             # The fulfillment
    ):

    # As it can be beneficial to produce beforehand for later deadlines,
    # overproduction should only be taken into acount on a total basis, not on a per-deadline basis

    # Filter only positive overproduction (otherwise underproduction)
    overproduction_filter = np.vectorize(lambda x: cpm_max((x,0)))

    # How much has been overproduced
    b = np.cumsum(bin_production.item_counts, axis=1)[:,-1] - np.cumsum(production_schedule.get_requirements(), axis=1)[:,-1]
    b = b.flatten()
    b = overproduction_filter(b)

    # Punish overproduction based on item value (its surface area)
    o = sum( b[i_item]*item.area for (i_item,item) in enumerate(production_schedule.items) )

    return o

def waste(
        bin_production : BinProduction,                 # The fulfillment
        single_bin_solutions : list[AbstractSingleBinPacking]   # The packings
    ):

    o = sum(
            (sbs.bin.area - sbs.area) *     # The wasted area
            sum(bin_production.bin_repeats[i_sbs,:])       # The repeated use of this wasted area
        for (i_sbs,sbs) in enumerate(single_bin_solutions))

    return o

def lower_left_preference(
        free_single_bins : list[AbstractSingleBinPacking]   # The new bins to pack
    ):
    #return cpm_sum([cpm_sum(np.multiply(item.pos_xs_arr + item.pos_ys_arr,item.active_arr).flatten()) for fsb in free_single_bins for item in fsb.items])


    # return cpm_sum([ cpm_sum(item.pos_xs_arr*item.active_arr) + cpm_sum(item.pos_ys_arr*item.active_arr) 
    #         for item in free_single_bins[0].items if ((len(item.pos_xs_arr.flatten()) != 0) and (len(item.pos_ys_arr.flatten()) != 0) and (len(item.active_arr.flatten()) != 0))])

    return cpm_sum([ cpm_sum( (item.pos_xs_arr + item.pos_ys_arr) * item.active_arr ) 
            for item in free_single_bins[0].items if ((len(item.pos_xs_arr.flatten()) != 0) and (len(item.pos_ys_arr.flatten()) != 0) and (len(item.active_arr.flatten()) != 0))])


    #return sum([sum((item.pos_xs+item.pos_ys)*item.active) for fsb in free_single_bins for item in fsb.items ])

def skewless_preference(
        free_single_bins : list[AbstractSingleBinPacking]   # The new bins to pack
    ):

    o = 0

    for item in free_single_bins[0].items:
        for i_length in range(item.nr_length_repeats()-1):
            for i_width in range(item.nr_width_repeats()):
                o += abs(item.pos_xs_arr[i_length, i_width] - item.pos_xs_arr[i_length+1, i_width])*item.active_arr[i_length, i_width]*item.active_arr[i_length+1, i_width]

    return -o

    #return cpm_sum([cpm_sum(np.multiply(item.pos_xs_arr + item.pos_ys_arr,item.active_arr).flatten()) for fsb in free_single_bins for item in fsb.items])


    # return cpm_sum([ cpm_sum(item.pos_xs_arr*item.active_arr) + cpm_sum(item.pos_ys_arr*item.active_arr) 
    #         for item in free_single_bins[0].items if ((len(item.pos_xs_arr.flatten()) != 0) and (len(item.pos_ys_arr.flatten()) != 0) and (len(item.active_arr.flatten()) != 0))])

    return cpm_sum([ cpm_sum( (item.pos_xs_arr + item.pos_ys_arr) * item.active_arr ) 
            for item in free_single_bins[0].items if ((len(item.pos_xs_arr.flatten()) != 0) and (len(item.pos_ys_arr.flatten()) != 0) and (len(item.active_arr.flatten()) != 0))])


    #return sum([sum((item.pos_xs+item.pos_ys)*item.active) for fsb in free_single_bins for item in fsb.items ])