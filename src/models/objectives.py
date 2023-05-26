from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking


def waste(sbp: AbstractSingleBinPacking):
    return \
        sbp.bin.area \
        - sbp.area
