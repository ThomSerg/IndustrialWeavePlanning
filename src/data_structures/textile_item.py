from dataclasses import dataclass

from src.data_structures.item import Item
from src.data_structures.color.composite_color import CompositeColor


@dataclass(kw_only=True)
class TextileItem(Item):

    '''
    A textile item to be woven.
    '''

    color: CompositeColor   # colour requirements of the textile

