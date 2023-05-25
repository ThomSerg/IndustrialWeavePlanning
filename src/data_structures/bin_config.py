from dataclasses import dataclass

@dataclass
class BinConfig:
    
    width: int
    min_length: int
    max_length: int
    min_packing_zone: int = None
    max_packing_zone: int = None

    def __post_init__(self):
        if self.min_packing_zone is None: self.min_packing_zone = 0
        if self.max_packing_zone is None: self.max_packing_zone = self.max_length
    
    def get_max_bin_area(self):
        return self.width*self.max_length