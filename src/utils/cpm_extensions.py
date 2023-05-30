from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname
from cpmpy.expressions.python_builtins import any

def intvar_1D(lower, upper, repeat=1):
    if repeat == 1:
        return cpm_array([intvar(lower, upper)])
    return intvar(lower, upper, repeat)