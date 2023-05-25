from dataclasses import dataclass

@dataclass
class MachineConfig:
    
    width: int
    min_length: int
    max_length: int
    max_creel_number: int = -1
    max_creel_colors: int = -1
    creel_switch_penalty: int = -1

    def get_max_bin_area(self):
        return self.width*self.max_length