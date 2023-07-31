from dataclasses import dataclass
from abc import ABC


@dataclass
class FixableObject(ABC):

    '''
    An object with a free decision variable, which can be fixed to return a normal python type.
    '''

    fixed: bool = False

    '''
    Fix the value
    '''
    def fix(self):
        self.fixed = True
        self._post_fix()
    
    '''
    Post fix extensions
    '''
    def _post_fix(self):
        pass

    '''
    Free the value
    '''
    def free(self):
        self.fixed = False
        self._post_free()

    '''
    Post free extensions
    '''
    def _post_free(self):
        pass
