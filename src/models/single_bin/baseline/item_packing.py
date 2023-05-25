from __future__ import annotations
from dataclasses import dataclass

from cpmpy.expressions.variables import NDVarArray, intvar, boolvar, cpm_array

from src.utils.fixable_object import FixableObject
import src.utils.fixable_type as ft

from src.data_structures.abstract_item_packing import AbstractItemPacking

@dataclass(kw_only=True)
class ItemPacking(AbstractItemPacking):

    max_count: int
    
    fixable_rotation: ft.FixableBoolArray = None

    def __post_init__(self):
        super().__post_init__()
        self.fixable_rotation = ft.FixableBoolArray(fixable_parent=self, free_value=boolvar(self.max_count))
          
    def get_variables(self):
        if self.max_count == 1:
            return super().get_variables() + [self.rotations]
        return super().get_variables() + list(self.rotations)
    
    @property
    def rotations(self):
        return self.fixable_rotation.value()

    @property
    def widths(self):
        return self.item.width * self.rotations + self.item.height * (1 - self.rotations)

    @property
    def heights(self):
        return self.item.height * self.rotations + self.item.width * (1 - self.rotations)    

    def _pos_xs_var(self):
        if (self.max_count == 1):
            return cpm_array([intvar(0, self.bin_config.width)])
        return intvar(0, self.bin_config.width, self.max_count)

    def _pos_ys_var(self):
        if (self.max_count == 1):
            return cpm_array([intvar(self.bin_config.min_packing_zone, self.bin_config.max_packing_zone)])
        return intvar(self.bin_config.min_packing_zone, self.bin_config.max_packing_zone, self.max_count)

    def _count_var(self):
        return intvar(0, self.max_count)
    
    def _active_var(self):
        return boolvar(self.max_count)

    def __eq__(self, other):
        if isinstance(other, ItemPacking):
            return (self.item == other.item) & (self.count == other.count)
        else:
            return False
