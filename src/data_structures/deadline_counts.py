from dataclasses import dataclass

import numpy.typing as npt


@dataclass
class DeadlineCounts:

    '''
    Collection of demands (or achieved production) for certain items across all deadlines.
    '''

    counts: npt.NDArray     # the demand

    def get_counts_for(self, deadline:int) -> npt.NDArray:
        return self.counts[:,deadline]

    def get_counts_untill(self, deadline:int):
        return self.counts[:,:deadline]