from ...single_bin.anchor.model import AnchorSBM

from src.data_structures.bin import Bin
from src.data_structures.machine_config import MachineConfig
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking

from src.extensions.creel.models.single_bin.anchor.model import CreelModel

from cpmpy import Model

class AnchorSBMCreel(AnchorSBM):

    # Constructor
    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: AbstractSingleBinPacking,
                    is_end_packing: bool = False
                ):

        super().__init__(machine_config, single_bin_packing, is_end_packing)

        self.creel_model = CreelModel(
            self.machine_config.max_creel_colors,
            self.single_bin_packing.items,
            self.single_bin_packing,
            self.machine_config
        )
    
    def get_constraints(self):
        self.constraints.extend(self.creel_model.get_constraints())
        return super().get_constraints()
    

    def get_name():
        return "AnchorSBM&Creel"