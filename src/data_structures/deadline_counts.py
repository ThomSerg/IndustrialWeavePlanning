from dataclasses import dataclass

import numpy.typing as npt
import numpy as np

@dataclass
class DeadlineCounts:

 
    counts: npt.NDArray

    def get_counts_for(self, deadline:int) -> npt.NDArray:
        return self.counts[:,deadline]

    def get_counts_untill(self, deadline:int):
        return self.counts[:,:deadline]