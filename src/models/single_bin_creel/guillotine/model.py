from __future__ import annotations

from ...single_bin.guillotine.model import GuillotineSBM

from src.models.abstract_model import AbstractSingleBinModel, constraint
from src.data_structures.bin import Bin
from src.data_structures.machine_config import MachineConfig
from ...single_bin.anchor.single_bin_packing import SingleBinPacking

from src.extensions.creel.models.single_bin.guillotine.model import CreelModel


class GuillotineSBMCreel(GuillotineSBM):

    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: SingleBinPacking,
                    is_end_packing: bool = False
                ):
        super().__init__(machine_config, single_bin_packing, is_end_packing)

        self.creel_model = CreelModel(
            self.machine_config.max_creel_colors,
            self.single_bin_packing.items,
            self,
            self.machine_config
        )

    def get_constraints(self):
        self.constraints.extend(self.creel_model.get_constraints())
        return super().get_constraints()
    
    def get_name():
        return "AnchorMBM&Creel"