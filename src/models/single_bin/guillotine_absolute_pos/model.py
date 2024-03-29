from __future__ import annotations

from cpmpy.expressions.python_builtins import sum as cpm_sum
from cpmpy.expressions.variables import intvar

from ..guillotine.model import GuillotineSBM
from ..anchor.single_bin_packing import SingleBinPacking
from ..anchor.item_packing import ItemPacking

from src.data_structures.bin import Bin
from src.models.abstract_model import constraint
from src.data_structures.machine_config import MachineConfig


class GuillotineAbsolutePosSBM(GuillotineSBM):

    '''
    CP-Guillotine-Absolute
    '''

    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: SingleBinPacking
                ):
        super().__init__(machine_config, single_bin_packing)

        # Additional absolute positional variables
        self.pos_xs = intvar(0, self.bin_width, (self.P ,self.A, self.B, self.I))
        self.pos_ys = intvar(0, self.single_bin_packing.bin.max_length , (self.P ,self.A, self.B, self.I))

    @classmethod
    def init_from_problem(cls, problem) -> GuillotineAbsolutePosSBM:

        sbp = SingleBinPacking(
                _items = problem.get_item_packing(ItemPacking),
                _items_rotated = problem.get_item_packing_rotated(ItemPacking),
                bin = Bin(config=problem.get_bin_config()),
            )
        
        return cls(
            problem.get_machine_config(),
            sbp,
        )
    
    def get_name():
        return "GuillotineAbsolute"
    
    @constraint
    def bin_length_link(self):
        return [self.single_bin_packing.bin.length == self.bin_length]
    
    @constraint
    def absolute_pos(self):
        c = []

        pattern_height = 0
        for p in range(self.P): # go over patterns
            strip_width = 0
            for a in range(self.A): # go over strips
                cut_height = 0
      
                for b in range(self.B): # go over vertical cuts
                    for i in range(self.I): # go over items

                        c.append(self.pos_xs[p,a,b,i] == strip_width)
                        c.append(self.pos_ys[p,a,b,i] == pattern_height+cut_height)
                    
                        cut_height += self.items[i].height*self.sigma[p,a,b,i]

                strip_width += sum(self.gamma[p,a,:]*self.widths) #max_width

            pattern_height += self.pattern_length[p]

        return c
    
    def get_constraints(self):
        c = []
        c.extend(self.guillotine_constraints())
        c.extend(self.bin_length_link())
        c.extend(self.absolute_pos())
        c.extend(self.constraints)
        self.constraints = c
        return c

    def get_variables(self):
        return super().get_variables() + self.pos_xs.flatten().tolist() + self.pos_ys.flatten().tolist()
    
    def get_objective(self):

        # Waste
        o1 = super().get_objective()

        # Preference for lower left corner
        o4 = cpm_sum([((item.pos_xs[i_instance] + item.pos_ys[i_instance])*(item.active[i_instance])) for item in self.single_bin_packing.items for i_instance in range(item.nr_length_repeats()*item.nr_width_repeats())])

        # Very large number
        B = self.single_bin_packing.bin.width*self.single_bin_packing.bin.max_length

        # Multi-objective objective function
        o = B*o1 + o4

        return o