from dataclasses import dataclass


@dataclass
class BinConfig:

    '''
    Configuration of a large object
    '''
    
    width: int          # width of the object
    min_length: int     # minimum length of the object
    max_length: int     # maximal length of the object
    
    def get_max_bin_area(self):
        return self.width*self.max_length