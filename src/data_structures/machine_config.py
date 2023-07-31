from dataclasses import dataclass


@dataclass
class MachineConfig:

    '''
    Configuration of the weaving machine.
    '''
    
    width: int                      # machine width
    min_length: int                 # production segment minimal length
    max_length: int                 # production segment maximal length
    max_creel_number: int = -1      # max number of creel sections
    max_creel_colors: int = -1      # max number of colours per dent
    creel_switch_penalty: int = -1  # delay caused by reconfiguring creel

    def get_max_bin_area(self):
        return self.width*self.max_length