from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class FixableObject(ABC):

    fixed: bool = False

    def fix(self):
        self.fixed = True
        self._post_fix()
    
    def _post_fix(self):
        pass

    def free(self):
        self.fixed = False
        self._post_free()

    def _post_free(self):
        pass
