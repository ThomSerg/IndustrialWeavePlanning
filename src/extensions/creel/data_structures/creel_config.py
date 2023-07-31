from dataclasses import dataclass


@dataclass(kw_only=True)
class CreelConfig:

    '''
    Configuration of the creel.
    '''

    total_width: int    # object width
    max_colors: int     # max number of colours per dent
    