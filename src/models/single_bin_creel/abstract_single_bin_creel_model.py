from __future__ import annotations
from abc import ABCMeta, abstractmethod

from src.extensions.creel.data_structures.creel_section import CreelSection


class AbstractSBMCreel(metaclass=ABCMeta):

    '''
    Abstract single bin model with creel support
    '''

    @abstractmethod
    def within_color_section(self, section: CreelSection):
        pass
