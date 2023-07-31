from __future__ import annotations
from dataclasses import dataclass
from abc import abstractmethod

from src.data_structures.item import Item
from src.data_structures.bin_config import BinConfig
from src.utils.fixable_object import FixableObject
import src.utils.fixable_type as ft



@dataclass(kw_only=True)
class AbstractItemPacking(FixableObject):
    '''
    Abstract class representing a packed item, i.e., an item which has been (or has to be)
    positioned inside a larger object.
    '''

    item: Item = None               # the item that is to be packed
    bin_config: BinConfig = None    # the config of the larger object to pack in
    rotation: bool = False          # the rotation (90°) of the item
    max_count: int = 0              # max on the number of instance copies

    fixable_pos_xs_arr: ft.FixableIntArray = None   # x-coordinate of set-of-points encoding
    fixable_pos_ys_arr: ft.FixableIntArray = None   # y-coordinate of set-of-points encoding

    fixable_count: ft.FixableInt = None             # how many instances are packed
    fixable_selected: ft.FixableBool = None         # if the item is packed at least once
    fixable_active: ft.FixableBoolArray = None      # which instances are active

    def __post_init__(self):

        # Initialise decision variables
        self.fixable_pos_xs_arr = ft.FixableIntArray(fixable_parent=self, free_value=self._pos_xs_var())   
        self.fixable_pos_ys_arr = ft.FixableIntArray(fixable_parent=self, free_value=self._pos_ys_var())
        self.fixable_count = ft.FixableInt(fixable_parent=self, free_value=self._count_var())
        self.fixable_selected = ft.FixableBool(fixable_parent=self)
        self.fixable_active = ft.FixableBoolArray(fixable_parent=self, free_value=self._active_var())

    def get_variables(self):
        return list(self.pos_xs) + list(self.pos_ys) + [self.count] + [self.selected] + list(self.active)

    # Properties

    @property
    def pos_xs_arr(self) -> ft.IntArray:
        return self.fixable_pos_xs_arr.value()
    
    @property
    def pos_ys_arr(self) -> ft.IntArray:
        return self.fixable_pos_ys_arr.value()

    @property
    def pos_xs(self) -> ft.IntArray:
        return self.pos_xs_arr.flatten()
    
    @property
    def pos_ys(self) -> ft.IntArray:
        return self.pos_ys_arr.flatten()
    
    @property
    @abstractmethod
    def rotations(self): pass
    
    @property
    @abstractmethod
    def widths(self): pass

    @property
    @abstractmethod
    def heights(self): pass

    @property
    def area(self):
        return self.item.area
    
    @property
    def count(self):
        return self.fixable_count.value()
    
    @property
    def active_arr(self):
        return self.fixable_active.value()
    
    @property
    def active(self):
        return self.active_arr.flatten()

    @property
    def selected(self) -> ft.Bool:
        return self.fixable_selected.value()
        
    # Generation of decision variables

    @abstractmethod
    def _pos_xs_var(): pass

    @abstractmethod
    def _pos_ys_var(): pass

    @abstractmethod
    def _count_var(): pass

    @abstractmethod
    def _active_var(): pass