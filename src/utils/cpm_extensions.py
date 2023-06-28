from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname
from cpmpy.expressions.python_builtins import any

def intvar_1D(lower, upper, repeat=1):
    if repeat == 1:
        return cpm_array([intvar(lower, upper)])
    return intvar(lower, upper, repeat)

def intvar_2D(lowers, uppers):
    vars = []
    for lower_row, upper_row in zip(lowers, uppers):
        temp_vars = []
        for lower, upper in zip(lower_row, upper_row):
            temp_vars.append(intvar(lower, upper))
        vars.append(temp_vars)

    if vars == []:
            vars = [[]]
            
    return cpm_array(vars)
