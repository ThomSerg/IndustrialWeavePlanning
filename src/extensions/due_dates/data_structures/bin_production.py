
from dataclasses import dataclass

from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname

import numpy as np
import numpy.typing as npt


from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking
from src.data_structures.production_schedule import ProductionSchedule

@dataclass(kw_only=True)
class BinProduction:

    deadline_betweens: npt.NDArray[np.int_] = None
    production_schedule: ProductionSchedule
    fixed_bin_packings: list[AbstractSingleBinPacking]
    fixable_bin_packings: list[AbstractSingleBinPacking]
    _item_counts: npt.NDArray[np.int_] = None       # [bin_solution x bin_item]


    #_max_bin_repeats: NDVarArray[intvar] = None     # [bin_solution x deadline]
    _max_new_bin_repeat: int = -1
    bin_repeats: NDVarArray[intvar] = None         # [bin_solution x deadline]

    bin_active: NDVarArray[boolvar] = None         # [bin_solution x deadline]
    bin_order: NDVarArray[intvar] = None           # [bin_solution x deadline]

    bin_delays_before: NDVarArray[intvar] = None          # [bin_solution x deadline]
    bin_delays_after: NDVarArray[intvar] = None           # [bin_solution x deadline]

    bin_starts: NDVarArray[intvar] = None           # [bin_solution x deadline]
    bin_ends: NDVarArray[intvar] = None             # [bin_solution x deadline]
    
    fixed = False
    

    def __post_init__(self):
        self.bin_packings = self.fixed_bin_packings + self.fixable_bin_packings

        if self.deadline_betweens is None: self.deadline_betweens = np.insert(np.ediff1d(self.deadlines), 0, self.deadlines[0]+1)

        if self._item_counts is None: self._item_counts = cpm_array([bin_packing.counts for bin_packing in self.bin_packings])
    
        if self.bin_repeats is None: self.bin_repeats = self._bin_repeats_var()
        if self.bin_active is None: self.bin_active = self._bin_active_var()
        if self.bin_order is None: self.bin_order = self._bin_order_var()

        if self.bin_delays_before is None: self.bin_delays_before = self._bin_delays_before_var()
        if self.bin_delays_after is None: self.bin_delays_after = self._bin_delays_after_var()

        # self.bin_delays_before_list = [ [[] for i_bin_solution in range(len(self.bin_packings))] for i_deadline in range(self.nr_deadlines)]
        # self.bin_delays_after_list = [ [[] for i_bin_solution in range(len(self.bin_packings))] for i_deadline in range(self.nr_deadlines)]   


        if self.bin_starts is None: self.bin_starts = self._bin_starts_var()
        if self.bin_ends is None: self.bin_ends = self._bin_ends_var()

        # # Get the start and end position of each bin section in terms of the total number of predecessing repeats
        # between_deadline_repeats = np.insert(self.deadline_betweens,0,0)
        # self.bin_starts = 
        # self.bin_ends = []

        # for i_deadline in range(len(self.deadlines)):
        #     self.bin_starts.append(
        #         np.array([
        #             self.bin_delays_before[i_bin,i_deadline] + sum(between_deadline_repeats[:i_deadline]) + sum([(self.bin_order[i_bin_other,i_deadline] < self.bin_order[i_bin,i_deadline])*(self.bin_repeats[i_bin_other,i_deadline]+self.bin_delays_before[i_bin_other,i_deadline]+self.bin_delays_after[i_bin_other,i_deadline]) for i_bin_other in range(len(self.bin_active)) if i_bin_other != i_bin]) 
        #             for i_bin in range(len(self.bin_active)) # TODO weten dat < order 0 nooit zal slagen
        #         ])
        #     )
        #     self.bin_ends.append(
        #         np.array([
        #             bin_start + bin_repeat-1 for (bin_start,bin_repeat) in zip(self.bin_starts[i_deadline],self.bin_repeats[:,i_deadline])
        #         ])
        #     )

        # self.bin_starts = cpm_array(np.array(self.bin_starts)).T
        # self.bin_ends = np.array(self.bin_ends).T

    @property
    def nr_deadlines(self):
        return len(self.deadlines)
    
    @property
    def nr_packings(self):
        return len(self.bin_packings)
    
    @property
    def nr_fixable_packings(self):
        return len(self.fixable_bin_packings)
    
    @property
    def nr_fixed_packings(self):
        return len(self.fixed_bin_packings)

    def get_variables(self):
        return self.bin_repeats + self.bin_active + self.bin_order + self.bin_delays_before  + self.bin_delays_after

    # def fix(self): # TODO
    #     self.fixed = True

    @property
    def deadlines(self) -> npt.NDArray[np.int_]:
        return self.production_schedule.deadlines

    @property
    def fixed_bin_active(self) -> NDVarArray[boolvar]:
        return self.bin_active[:self.nr_fixed_packings]
    
    @property
    def fixable_bin_active(self) -> NDVarArray[boolvar]:
        return self.bin_active[-self.nr_fixable_packings:]

    @property
    def item_counts(self):
        return np.matmul(self.bin_repeats.copy().T,self._item_counts).T 

    def _bin_repeats_var(self):
        res = []
        for deadline_between in self.deadline_betweens:
            if self.nr_packings > 1:
                res.append(intvar(0, deadline_between, self.nr_packings))
            else:
                res.append(cpm_array([intvar(0, deadline_between)]))
        return cpm_array(np.array(res)).T
    
    def _bin_active_var(self):
        return boolvar(shape=(self.nr_packings, self.nr_deadlines))

    def _bin_order_var(self):
        return intvar(0, self.nr_packings-1, shape=(self.nr_packings, self.nr_deadlines))

    def _bin_delays_before_var(self):
        return intvar(0, self.deadlines[-1]-1, shape=(self.nr_packings, self.nr_deadlines)) # TODO kan strikter

    def _bin_delays_after_var(self):
        return intvar(0, self.deadlines[-1]-1, shape=(self.nr_packings, self.nr_deadlines))
    
    def _bin_starts_var(self):
        return intvar(0, self.deadlines[-1], shape=(self.nr_packings, self.nr_deadlines))
    
    def _bin_ends_var(self):
        return intvar(0, self.deadlines[-1], shape=(self.nr_packings, self.nr_deadlines))
    
    def print_stats(self):
        print("Bins")
        print(np.array([self.bin_starts, self.bin_ends]).T)
        print(self.bin_active)
        print(self.bin_order)


def intvarlu(lb:npt.NDArray[np.int_], ub:npt.NDArray[np.int_], shape=1, name=None):
    # create base data
    data = np.array([_IntVarImpl(lb[idxs],ub[idxs], name=_genname(name, idxs)) for idxs in np.ndindex(shape)]) # repeat new instances
    # insert into custom ndarray
    return NDVarArray(shape, dtype=object, buffer=data)