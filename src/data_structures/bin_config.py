from dataclasses import dataclass

@dataclass
class BinConfig:
    
    width: int
    min_length: int
    max_length: int
    
    def get_max_bin_area(self):
        return self.width*self.max_length