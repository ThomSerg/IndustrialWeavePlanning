from __future__ import annotations
from abc import ABCMeta, abstractmethod

from src.extensions.creel.data_structures.creel_section import CreelSection
from src.models.abstract_model import AbstractModel


class AbstractSBMCreel(metaclass=ABCMeta):

    @abstractmethod
    def within_color_section(self, section: CreelSection):
        pass
