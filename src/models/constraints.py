

def non_overlap(pxs_1, pys_1, w_1, h_1, pxs_2, pys_2, w_2, h_2):
    return \
        (pxs_1 + w_1 <= pxs_2) | \
        (pxs_2 + w_2 <= pxs_1) | \
        (pys_1 + h_1 <= pys_2) | \
        (pys_2 + h_2 <= pys_1)