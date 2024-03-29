from __future__ import annotations

import numpy as np
import numpy.typing as npt

from src.data_structures.problem.multi_bin_problem import MultiBinProblem
from src.data_structures.problem.colored_single_bin_problem import ColoredSingleBinProblem
from src.data_structures.problem.colored_multi_bin_problem import ColoredMultiBinProblem
from src.data_structures.problem.single_bin_problem import SingleBinProblem

from src.data_structures.color.color_collection import ColorCollection
from src.data_structures.color.composite_color import CompositeColor
from src.data_structures.color import color

class ProblemJsonCM(ColoredMultiBinProblem):
    def __init__(self, name, json_dict):
        self.json_dict = json_dict
        self.name = name
        self.widths : npt.NDArray[np.int_] = np.array(json_dict["widths"],dtype='int64')
        self.heights : npt.NDArray[np.int_] = np.array(json_dict["heights"],dtype='int64')
        self.deadlines : npt.NDArray[np.int_] = np.array(json_dict["deadlines"],dtype='int64')
        self.deadline_counts : npt.NDArray[np.int_] = np.array(json_dict["deadline_counts"],dtype='int64')
        self.colors : npt.NDArray[np.int_] = np.array(json_dict["colors"],dtype='int64')
        self.machine_width : int = json_dict["machine_config"]["width"]
        self.machine_min_length : int = json_dict["machine_config"]["min_length"]
        self.machine_max_length : int = json_dict["machine_config"]["max_length"]
        self.max_creel_number: int = json_dict["machine_config"]["max_creel_number"]
        self.max_creel_colors: int = json_dict["machine_config"]["max_creel_colors"]
        self.color_collection = ColorCollection(composite_colors=[
            CompositeColor(0, [color.RED]),
            CompositeColor(1, [color.GREEN]),
            CompositeColor(2, [color.BLUE]),
            CompositeColor(3, [color.PURPLE]),
            CompositeColor(4, [color.CYAN]),
        ])
        self.creel_switch_penalty : int = json_dict["machine_config"]["creel_switch_penalty"]

    @classmethod
    def init_from_file(cls, json_dict) -> list[ProblemJsonCM]:
        return [cls(a, json_dict[a]) for a in json_dict]

class ProblemJsonCS(ColoredSingleBinProblem):
    def __init__(self, name, json_dict):
        self.json_dict = json_dict
        self.name = name
        self.widths : npt.NDArray[np.int_] = np.array(json_dict["widths"],dtype='int64')
        self.heights : npt.NDArray[np.int_] = np.array(json_dict["heights"],dtype='int64')
        self.colors : npt.NDArray[np.int_] = np.array(json_dict["colors"],dtype='int64')
        self.machine_width : int = json_dict["machine_config"]["width"]
        self.machine_min_length : int = json_dict["machine_config"]["min_length"]
        self.machine_max_length : int = json_dict["machine_config"]["max_length"]
        self.max_creel_number: int = 1#json_dict["machine_config"]["max_creel_number"]
        self.max_creel_colors: int = json_dict["machine_config"]["max_creel_colors"]
        self.color_collection = ColorCollection(composite_colors=[
            CompositeColor(0, [color.RED]),
            CompositeColor(1, [color.GREEN]),
            CompositeColor(2, [color.BLUE]),
            CompositeColor(3, [color.PURPLE]),
            CompositeColor(4, [color.CYAN]),
        ])
        self.creel_switch_penalty = 0

    @classmethod
    def init_from_file(cls, json_dict) -> list[ProblemJsonCS]:
        return [cls(a, json_dict[a]) for a in json_dict]
    
class ProblemJsonS(SingleBinProblem):
    def __init__(self, name, json_dict):
        self.json_dict = json_dict
        self.name = name
        self.widths : npt.NDArray[np.int_] = np.array(json_dict["widths"],dtype='int64')
        self.heights : npt.NDArray[np.int_] = np.array(json_dict["heights"],dtype='int64')
        self.machine_width : int = json_dict["machine_config"]["width"]
        self.machine_min_length : int = json_dict["machine_config"]["min_length"]
        self.machine_max_length : int = json_dict["machine_config"]["max_length"]

    @classmethod
    def init_from_file(cls, json_dict) -> list[ProblemJsonS]:
        return [cls(a, json_dict[a]) for a in json_dict]

class ProblemJsonM(MultiBinProblem):
    def __init__(self, name, json_dict):
        self.json_dict = json_dict
        self.name = name
        self.widths : npt.NDArray[np.int_] = np.array(json_dict["widths"],dtype='int64')
        self.heights : npt.NDArray[np.int_] = np.array(json_dict["heights"],dtype='int64')
        self.deadlines : npt.NDArray[np.int_] = np.array(json_dict["deadlines"],dtype='int64')
        self.deadline_counts : npt.NDArray[np.int_] = np.array(json_dict["deadline_counts"],dtype='int64')
        self.machine_width : int = json_dict["machine_config"]["width"]
        self.machine_min_length : int = json_dict["machine_config"]["min_length"]
        self.machine_max_length : int = json_dict["machine_config"]["max_length"]


    @classmethod
    def init_from_file(cls, json_dict) -> list[ProblemJsonS]:
        return [cls(a, json_dict[a]) for a in json_dict]