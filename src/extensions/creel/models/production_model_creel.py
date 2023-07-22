
from src.extensions.due_dates.models.production_model import ProductionModel
from src.models.multi_bin.lns.model import ProductionModelLNS

from src.data_structures.machine_config import MachineConfig
from src.data_structures.production_schedule import ProductionSchedule
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking

from src.models.abstract_model import AbstractSingleBinModel
from src.data_structures.abstract_item_packing import AbstractItemPacking

from .multi_bin.model import CreelModel


class ProductionModelCreel(ProductionModelLNS):

    # Constructor
    def __init__(self,
                    machine_config: MachineConfig,
                    production_schedule: ProductionSchedule,
                    fixed_single_bins: list[AbstractSingleBinPacking],
                    free_single_bins: list[AbstractSingleBinPacking],
                    items: list[AbstractItemPacking],
                    single_bin_model: AbstractSingleBinModel,
                ):
        super().__init__(machine_config, production_schedule, fixed_single_bins, free_single_bins, items, single_bin_model)

        self.creel_model = CreelModel(
            max_creel_number=self.machine_config.max_creel_number,
            max_deadline=self.production_schedule.deadlines[-1],
            max_colors=self.machine_config.max_creel_colors,
            items=self.items,
            fixed_single_bin_packings=self.fixed_single_bins,
            single_bin_model=self.free_single_bin_models[0] if len(self.free_single_bin_models) != 0 else [],
            bin_production=self.bin_production,
            machine_config=self.machine_config
        )

    def get_constraints(self):
        self.constraints.extend(self.creel_model.get_constraints())
        return super().get_constraints()
