from ...single_bin.anchor.model import AnchorSBM

from src.data_structures.bin import Bin
from src.data_structures.machine_config import MachineConfig
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking

from src.extensions.creel.models.single_bin.model import CreelModel

from cpmpy import Model

class AnchorSBMCreel(AnchorSBM):

    # Constructor
    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: AbstractSingleBinPacking,
                    is_end_packing: bool = False
                ):

        # Save the provided arguments as attributes
        self.machine_config = machine_config
        self.single_bin_packing = single_bin_packing
        self.is_end_packing = is_end_packing

        # CPMpy model data
        self.constraints = []
        self.objective = 0
        self.model = Model()

        # To collect data about the algorithm
        self.stats = {}

        self.creel_model = CreelModel(
            self.machine_config.max_creel_colors,
            self.single_bin_packing.items,
            self.single_bin_packing,
            self.machine_config
        )

    # Alternative constructor from problem formulation
    @classmethod
    def init_from_problem(cls, problem) -> AnchorSBM:
        # Create packing variables
        sbp = cls.single_bin_packing(
                _items=problem.get_item_packing(cls.ItemPacking),
                _items_rotated=problem.get_item_packing_rotated(cls.ItemPacking),
                bin=Bin(config=problem.get_bin_config()),
            )
        # Construct the model
        return cls(
            problem.get_machine_config(),
            sbp,
            True
        )
    
    def get_constraints(self):
        self.constraints.extend(self.creel_model.get_constraints())
        return super().get_constraints()
    

    def get_name():
        return "Anchor&Creel"